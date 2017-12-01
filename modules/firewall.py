""" A module to manage whitelist/blacklist IP sets. """
from gluon import current
from gluon import Field
import zero


MAX = 4
logger = zero.getLogger('app')

class Blacklist(object):
    """ Manage the blacklist IP set. """

    def __init__(self, db):
        """ Define blacklist table. """
        self.db = db
        db.define_table(
            'black',
            Field('country'),
            Field('org'),
            Field('src'),
            Field('timestamp', 'datetime', default=current.request.now),
            Field('urls', 'list:string'),
            Field('whois'))

    def add(self, src):
        """ Add an address to the blacklist IP set. """
        import xmlrpclib

        try:
            ipsetd = xmlrpclib.ServerProxy('http://localhost:8001')
            ipsetd.add('blacklist', src)
        except:
            logger.exception('Blacklist error')

    def insert(self, src, urls):
        """ Insert a new row into the blacklist table and return it. """
        from subprocess import check_output

        # Query whois and parse data out of it.
        whois = ''
        org = 'Unknown'
        country = 'Unknown'
        try:
            whois = check_output('whois %s' % src, shell=True)
            for line in whois.splitlines():
                lower = line.lower()

                # Organisation.
                if org == 'Unknown':
                    if lower.startswith('org'):
                        tmp = line.split(':')[1].strip()
                        if tmp:
                            org = tmp
                    elif lower.startswith('descr'):
                        tmp = line.split(':')[1].strip()
                        if tmp:
                            org = tmp

                # Country.
                if country == 'Unknown':
                    if lower.startswith('country:'):
                        tmp = line.split(':')[1].strip()
                        if tmp:
                            country = tmp
        except:
            logger.exception('Bad whois request')

        # Add and return a new record.
        return self.db.black.insert(
            country=country,
            org=org,
            src=src,
            urls=urls,
            whois=whois)

    def email(self, row):
        """ Email the admin. """
        import socket
        from gluon.tools import Mail

        hostname = socket.gethostname()
        subject = 'Blacklist event on %s' % hostname
        mailer = Mail('localhost:25', 'noreply@%s' % hostname, tls=False)
        admin = self.db(self.db.auth_user).select().first()
        msg = '%s %s %s\n\n%s' % (row.src, row.org, row.country, row.whois)
        if admin and admin.email:
            mailer.send(admin.email, subject, msg)
            logger.info('Blacklist email sent to %s', admin.email)
        else:
            logger.error('Error finding app admin email address')

    def log(self, event, request_url):
        """ Log a blacklist event and ban the address when a threshold
        is reached. """

        # Update db or cache with the new request.
        src = current.request.env.remote_addr
        logger.warning('Logging %s %s from %s', event, request_url, src)
        row = self.db(self.db.black.src == src).select().first()
        if row:
            row.urls += (src, event, request_url)
            urls = row.urls
            row.update_record()
        else:
            urls = current.cache.ram('events-%s' % src, lambda: [])
            urls.append((src, event, request_url))
            urls = current.cache.ram('events-%s' % src, lambda: urls, 0)

        # Blacklist the IP when max threshold is reached. TODO scheduler.
        if len(urls) >= MAX:
            if not row:
                row = self.insert(src, urls)
                self.email(row)
            self.add(src)

class Whitelist(object):
    """ Manage the whitelist IP set. """

    def add(self, addr):
        """ Add an address to the whitelist. """
        import xmlrpclib

        try:
            fwd = xmlrpclib.ServerProxy('http://localhost:8001')
            fwd.add('whitelist', addr)
            current.response.flash = 'Whitelisted %s' % addr
        except Exception, err:
            if 'already added' in str(err):
                current.response.flash = 'Already whitelisted %s' % addr
            else:
                logger.exception('Whitelist error')
                current.response.flash = 'Error whitelisting address'

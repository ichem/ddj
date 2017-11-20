""" A module to manage whitelist/blacklist IP sets. """
import logging
from gluon import current
from gluon import Field
import zero


logger = zero.getLogger('app')

class Blacklist(object):
    """ Manage the blacklist. """

    def __init__(self, db):
        """ Define ban table. """
        self.db = db
        db.define_table(
            'bans',
            Field('country'),
            Field('src'),
            Field('timestamp', 'datetime', default=current.request.now),
            Field('urls', 'list:string'),
            Field('whois'))

    def log(self, event, request_url):
        """ Log a blacklist event and ban the address when a threshold
        is reached. """

        # Update db or cache with the new request.
        src = current.request.env.remote_addr
        logger.warning('Logging %s %s from %s', event, request_url, src)
        row = self.db(self.db.bans.src == src).select().first()
        if row:
            row.urls += (src, event, request_url)
            urls = row.urls
            row.update_record()
        else:
            urls = current.cache.ram('events-%s' % src, lambda: [])
            urls.append((src, event, request_url))
            urls = current.cache.ram('events-%s' % src, lambda: urls, 0)

        # Blacklist the IP when a threshold is reached.
        # TODO schedule all that follows.
        if not row and len(urls) == 4:
            import socket
            from subprocess import check_output
            from gluon.tools import Mail

            # Add a db record.
            country = 'Unknown'
            whois = ''
            try:
                whois = check_output('whois %s' % src, shell=True)
                for line in whois.splitlines():
                    if country == 'Unknown' and line.startswith('country:'):
                        tmp = line.replace('country:', '').strip()
                        if tmp:
                            country = tmp
                        continue
            except:
                logger.exception('Bad whois request')
            self.db.bans.insert(
                country=country,
                src=src,
                urls=urls,
                whois=whois)

            # Email the admin.
            hostname = socket.gethostname()
            subject = 'Ban event on %s' % hostname
            mailer = Mail('localhost:25', 'noreply@%s' % hostname, tls=False)
            admin = self.db(self.db.auth_user).select().first()
            msg = src + ' ' + country + '\n\n' + whois
            if admin and admin.email:
                mailer.send(admin.email, subject, msg)
                logger.info('Ban email sent to %s', admin.email)
            else:
                logger.error('Error finding app admin email address')

        # Do firewall.
        if len(urls) >= 4:
            import xmlrpclib

            try:
                fwd = xmlrpclib.ServerProxy('http://localhost:8001')
                fwd.add('blacklist', src)
            except:
                logger.exception('Blacklist error')

class Whitelist(object):
    """ Manage the firewall whitelist. """

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

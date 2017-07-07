def user():
    response.title = auth_title()
    return dict(form=auth())

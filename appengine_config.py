from gaesessions import SessionMiddleware
def webapp_add_wsgi_middleware(app):
	app = SessionMiddleware(app, cookie_key="d203aanewj320-09aasmfweppierwas9f823489efa/v,vmas;dfa-9s8fddf")
	return app

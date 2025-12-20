from app import app

if __name__ == "__main__":
	app.run()
else:
	wsgi_app = app

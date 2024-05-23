from flask import Flask, request

# init flask
app = Flask(__name__)

@app.route('/')
def main():
	return '<html><body><h1>Hello!</h1></body></html>'

@app.route('/upload', methods=['PUT'])
def upload():
	file = request.files['file']
	print(file.filename)
	file.save('/tmp/pycast/' + file.filename)
	return 'Upload successful!'

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)

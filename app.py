from flask import Flask
from flask_cors import CORS
from endpoints.generate import router as router_ai
from endpoints.embeddings import router as router_embeddings
from endpoints.conversation import router as router_conversation

app = Flask(__name__)
CORS(app)

app.register_blueprint(router_ai, url_prefix='/generate')
app.register_blueprint(router_embeddings, url_prefix='/embeddings')
app.register_blueprint(router_conversation, url_prefix='/conversation')

@app.route("/")
def index():
    return "OK"

if __name__ == "__main__":
    app.run(debug=True)

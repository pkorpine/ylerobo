from pathlib import Path
from sanic import Sanic, response
from .database import Database
from .yledl import get_title, get_program_id_and_url

app = Sanic("ylerobo")


@app.route("/api/add")
async def add(request):
    program = request.args["program"][0]
    freq = request.args["freq"][0]
    program_id, url = get_program_id_and_url(program)
    title = get_title(url)
    if not request.app.ctx.db.add(program_id, url, title, freq):
        return response.json({"status": "Error"}, status=406)
    return response.json({"status": "Ok", "program_id": program_id, "title": title})


@app.route("/api/remove")
async def remove(request):
    program = request.args["program"][0]
    program_id, _ = get_program_id_and_url(program)
    if not request.app.ctx.db.remove(program_id):
        return response.json({"status": "Error"}, status=406)
    return response.json({"status": "Ok"})


@app.route("/api/list")
async def list(request):
    ret = []
    for series in request.app.ctx.db.list():
        ret.append(
            {
                "program_id": series["program_id"],
                "url": series["webpage"],
                "title": series["title"],
                "freq": series["freq"],
                "last_check": str(series["last_check"]),
            }
        )
    return response.json(ret)


HTML_DIR = Path(__file__).parent / "html"
app.static("/", HTML_DIR.joinpath("index.html"), name="static_root")
app.static("/libs", HTML_DIR.joinpath("libs"), name="static_libs")


@app.route("/zz")
async def test(request):
    return await response.file("html/index.html")


@app.before_server_start
async def attach_db(app, loop):
    app.ctx.db = Database()


def serve(host="0.0.0.0", port=8000, debug=False):
    app.run(host=host, port=port, debug=debug, single_process=True)


if __name__ == "__main__":
    serve(debug=True)

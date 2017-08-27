from flask import abort, jsonify, request
from labelserver import app, printers, parser
import webargs.fields


@app.route("/api/printers/<printer_id>")
def api_printer(printer_id):
    printer = printers.get(printer_id) or abort(404)
    return jsonify({
        "id": printer.id,
        "label_types": {t.id: jsonify_label_type(t) for t in printer.label_types.values()}
    })


post_job_args = {
    "type": webargs.fields.String(required=True, allow_none=False, location="query")
}


@app.route("/api/printers/<printer_id>/jobs", methods=["GET", "POST"])
def api_printer_jobs(printer_id):
    printer = printers.get(printer_id) or abort(404)
    if request.method == "GET":
        return jsonify([jsonify_job(job) for job in printer.jobs()])
    else:
        args = parser.parse(post_job_args)
        label_type = printer.label_types.get(args["type"])
        if not label_type:
            abort(400)
        job = label_type.prepare(request.get_json())
        printer.add_job(job)
        return jsonify(jsonify_job(job))


def jsonify_job(job):
    return {
        "id": job.id,
        "status": job.status.name,
        "creation_time": job.creation_time,
        "data": job.data
    }

def jsonify_label_type(label_type):
    return {
        "id": label_type.id,
        "name": label_type.name
    }

from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import os
import time

app = Flask(__name__)
app.secret_key = "secretkey" 


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/demo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

UPLOAD_FOLDER = "static/uploads/category"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    image = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f"<Category {self.name}>"


@app.route("/")
def index():
    page = request.args.get('page', 1, type=int)
    categories = Category.query.paginate(page=page, per_page=10)
    return render_template("index.html", categories=categories)


@app.route("/create", methods=["GET", "POST"])
def create_category():
    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        file = request.files.get("image")

        filename = None
        if file:
            ext = file.filename.rsplit(".", 1)[-1].lower()
            filename = str(int(time.time())) + "." + ext
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        category = Category(
            name=name,
            description=description,
            image=f"{UPLOAD_FOLDER}/{filename}" if filename else None,
        )
        db.session.add(category)
        db.session.commit()

        flash("Category Created Successfully", "success")
        return redirect(url_for("index"))

    return render_template("create.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_category(id):
    category = Category.query.get_or_404(id)

    if request.method == "POST":
        category.name = request.form["name"]
        category.description = request.form["description"]
        file = request.files.get("image")

        if file:
            ext = file.filename.rsplit(".", 1)[-1].lower()
            filename = str(int(time.time())) + "." + ext
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            category.image = f"{UPLOAD_FOLDER}/{filename}"

        db.session.commit()
        flash("Category Updated Successfully", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", category=category)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_category(id):
    category = Category.query.get_or_404(id)
    db.session.delete(category)
    db.session.commit()
    flash("Category Deleted Successfully", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)

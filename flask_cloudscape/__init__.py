"""
Flask-Cloudscape Extension
==========================
A Flask extension that integrates AWS Cloudscape Design System components
into Flask + Jinja2 applications via Web Components.

Usage::

    from flask_cloudscape import Cloudscape

    app = Flask(__name__)
    cloudscape = Cloudscape()
    cloudscape.init_app(app)

    # Or, using the factory pattern:
    cloudscape = Cloudscape(app)

Once initialized, Cloudscape Jinja macros become available in all templates::

    {% from "cloudscape/_macros.html" import cs_button, cs_alert %}
    {{ cs_button(variant="primary", text="Submit") }}

The extension also auto-registers a Blueprint that serves the bundled
JS and CSS assets from its own static folder.
"""

import os
from flask import Blueprint

__version__ = "1.0.0"


class Cloudscape:
    """Flask extension for Cloudscape Design System integration.

    Registers a Blueprint named ``cloudscape`` that:
    - Serves pre-built JS/CSS bundles from ``flask_cloudscape/static/``
    - Exposes Jinja2 templates from ``flask_cloudscape/templates/``
    - Injects ``cloudscape_assets()`` helper into all templates

    Parameters
    ----------
    app : Flask, optional
        Flask application instance. If provided, ``init_app`` is called
        immediately. Pass ``None`` to use the factory pattern.
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Initialize the Cloudscape extension with a Flask app.

        Parameters
        ----------
        app : Flask
            The Flask application to register with.
        """
        # Determine paths relative to this file
        package_dir = os.path.dirname(os.path.abspath(__file__))
        static_dir = os.path.join(package_dir, "static")
        template_dir = os.path.join(package_dir, "templates")

        # Create the blueprint
        cloudscape_bp = Blueprint(
            "cloudscape",
            __name__,
            static_folder=static_dir,
            static_url_path="/cloudscape/static",
            template_folder=template_dir,
        )

        app.register_blueprint(cloudscape_bp)

        # Inject helper functions into Jinja2 global context
        @app.context_processor
        def inject_cloudscape_helpers():
            """Make Cloudscape asset helpers available in all templates."""
            from flask import url_for as flask_url_for
            from markupsafe import Markup

            def cloudscape_css():
                """Return the <link> tag for Cloudscape CSS."""
                url = flask_url_for("cloudscape.static", filename="css/cloudscape-adapter.css")
                return Markup(f'<link rel="stylesheet" href="{url}">')

            def cloudscape_js():
                """Return the <script> tag for Cloudscape JS."""
                url = flask_url_for("cloudscape.static", filename="js/cloudscape-adapter.js")
                return Markup(f'<script src="{url}"></script>')

            def cloudscape_assets():
                """Return both CSS and JS tags for Cloudscape."""
                return Markup(f"{cloudscape_css()}\n{cloudscape_js()}")

            def cs_render(comp_name, children=None, **kwargs):
                """Dynamically render any Cloudscape component by its snake_case name."""
                from flask_cloudscape.components import COMPONENTS
                comp_cls = COMPONENTS.get(comp_name.lower())
                if not comp_cls:
                    # Fallback to dynamic tag rendering
                    from flask_cloudscape.components import CloudscapeComponent
                    comp_cls = type(comp_name, (CloudscapeComponent,), {
                        "tag": f"cloudscape-{comp_name.lower().replace('_', '-')}"
                    })
                return comp_cls(children=children, **kwargs).render()

            return {
                "cloudscape_css": cloudscape_css,
                "cloudscape_js": cloudscape_js,
                "cloudscape_assets": cloudscape_assets,
                "cs_render": cs_render,
            }

        # Store reference on app for potential later access
        app.extensions = getattr(app, "extensions", {})
        app.extensions["cloudscape"] = self


if __name__ == "__main__":
    import json
    from flask import Flask, render_template

    app = Flask(__name__)
    cloudscape = Cloudscape(app)

    # Load 113 categorized components
    cat_path = os.path.join(os.path.dirname(__file__), "categories_113.json")
    with open(cat_path, "r") as f:
        categories = json.load(f)

    # Build flat dictionary of all components for fast lookup & sidebar listing
    all_components = []
    comp_by_slug = {}
    comp_category_map = {}

    def _to_pascal(s):
        return "".join(w.title() for w in s.replace("-", "_").split("_"))

    for cat in categories:
        for comp in cat["components"]:
            comp["python_class"] = _to_pascal(comp["slug"])
            all_components.append(comp)
            comp_by_slug[comp["slug"]] = comp
            comp_category_map[comp["slug"]] = cat

    # Load 59 patterns
    pat_path = os.path.join(os.path.dirname(__file__), "patterns_59.json")
    with open(pat_path, "r") as f:
        patterns_data = json.load(f)

    # Group patterns by subcategory
    pattern_groups = {}
    for p in patterns_data:
        subcat = p.get("subcategory", "General UI")
        if subcat not in pattern_groups:
            pattern_groups[subcat] = []
        pattern_groups[subcat].append(p)

    @app.route("/")
    def index():
        return render_template("cloudscape/catalogue.html", categories=categories)

    @app.route("/patterns")
    def patterns_view():
        return render_template(
            "cloudscape/patterns.html",
            pattern_groups=pattern_groups,
            patterns_data=patterns_data,
            total_patterns=len(patterns_data)
        )

    @app.route("/components/<slug>")
    def component_detail(slug):
        from flask import abort
        comp = comp_by_slug.get(slug)
        if not comp:
            abort(404)
        cat = comp_category_map.get(slug)
        return render_template(
            "cloudscape/component_detail.html",
            comp=comp,
            category=cat,
            all_components=all_components
        )

    port = int(os.environ.get("PORT", 5001))
    print(f" * Starting Flask-Cloudscape demo server on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)

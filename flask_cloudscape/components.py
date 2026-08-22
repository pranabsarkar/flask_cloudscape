"""
Cloudscape Python Components
=============================
Server-side Python classes that render Cloudscape Web Component HTML.

Each class maps 1:1 to a ``<cloudscape-*>`` custom element. Props are
converted from Python kwargs to kebab-case HTML attributes. Complex
values (dicts, lists) are auto-serialized to JSON.

This module dynamically registers classes for all 95+ Cloudscape components.
"""

import json
import re
import sys
from markupsafe import Markup


def _camel_to_kebab(name):
    """Convert camelCase or snake_case to kebab-case."""
    name = name.replace("_", "-")
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1).lower()


def _serialize_attr_value(value):
    """Serialize a Python value into an HTML attribute string."""
    if value is True:
        return ""
    if value is False or value is None:
        return None
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return str(value)


class CloudscapeComponent:
    """Base class for all Cloudscape Web Components."""
    tag = "cloudscape-component"

    def __init__(self, children=None, **kwargs):
        self.children = children
        self.props = kwargs

    def render(self):
        """Render the component to an HTML string."""
        attrs = []
        for key, value in self.props.items():
            attr_name = _camel_to_kebab(key)
            attr_value = _serialize_attr_value(value)
            if attr_value is None:
                continue
            if attr_value == "":
                attrs.append(attr_name)
            else:
                escaped = attr_value.replace("&", "&amp;").replace('"', "&quot;")
                attrs.append(f'{attr_name}="{escaped}"')

        attr_str = " " + " ".join(attrs) if attrs else ""
        children_html = str(self.children) if self.children is not None else ""

        return Markup(f"<{self.tag}{attr_str}>{children_html}</{self.tag}>")

    def __html__(self):
        return self.render()

    def __str__(self):
        return self.render()

    def __repr__(self):
        return f"<{self.__class__.__name__} tag={self.tag}>"


# ---------------------------------------------------------------------------
# Dynamic Component Class Generation (95+ components)
# ---------------------------------------------------------------------------

COMPONENT_NAMES = [
    "action_card", "alert", "anchor_navigation", "annotation_context", "app_layout",
    "app_layout_toolbar", "area_chart", "attribute_editor", "autosuggest", "avatar",
    "badge", "bar_chart", "board", "board_item", "box", "breadcrumb_group", "button",
    "button_dropdown", "button_group", "calendar", "cards", "checkbox", "code_editor",
    "code_view", "collection_preferences", "column_layout", "container", "content_layout",
    "copy_to_clipboard", "date_input", "date_picker", "date_range_picker", "divider",
    "drawer", "dropdown", "error_boundary", "expandable_section", "file_dropzone",
    "file_input", "file_token_group", "file_upload", "flashbar", "form", "form_field",
    "grid", "header", "help_panel", "hotspot", "icon", "icon_provider", "input",
    "item_card", "key_value_pairs", "line_chart", "link", "list", "live_region",
    "mixed_line_bar_chart", "modal", "multiselect", "navigable_group", "pagination",
    "panel_layout", "pie_chart", "popover", "progress_bar", "prompt_input", "property_filter",
    "radio_button", "radio_group", "s3_resource_selector", "segmented_control", "select",
    "side_navigation", "skeleton", "slider", "space_between", "spinner", "split_panel",
    "status_indicator", "steps", "support_prompt_group", "table", "tabs", "tag_editor",
    "textarea", "text_content", "text_filter", "tiles", "time_input", "toggle",
    "toggle_button", "token", "token_group", "tooltip", "top_navigation", "tree_view",
    "truncated_text", "tutorial_panel", "wizard"
]


def _to_pascal_case(snake_str):
    return "".join(x.title() for x in snake_str.split("_"))


# Register all components dynamically in the module
COMPONENTS = {}

for name in COMPONENT_NAMES:
    class_name = _to_pascal_case(name)
    tag_name = f"cloudscape-{name.replace('_', '-')}"
    
    # Custom base class or overrides if needed
    if class_name == "Button":
        # Keep Button constructor override to alias text as children
        class Button(CloudscapeComponent):
            tag = "cloudscape-button"
            def __init__(self, text=None, children=None, **kwargs):
                super().__init__(children=text or children, **kwargs)
        cls = Button
    else:
        # Create standard class dynamically
        cls = type(
            class_name,
            (CloudscapeComponent,),
            {
                "tag": tag_name,
                "__doc__": f"Cloudscape {class_name} Web Component helper."
            }
        )
    
    # Expose in global scope so they can be imported directly
    globals()[class_name] = cls
    COMPONENTS[name] = cls
    # Also support alternate lowercase key
    COMPONENTS[class_name.lower()] = cls

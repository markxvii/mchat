from flask import flash
from bleach import clean,linkify
from markdown import markdown

def flash_errors(form):
    for field,errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" %(
                getattr(form,field).label.text,error
            ))


def to_html(raw):

    allowed_tags = ['a', 'abbr', 'b', 'br', 'blockquote', 'code',

                    'del', 'div', 'em', 'img', 'p', 'pre', 'strong',

                    'span', 'ul', 'li', 'ol']

    allowed_attributes = ['src', 'title', 'alt', 'href', 'class']

    html = markdown(raw, output_format='html')

    clean_html = clean(html, tags=allowed_tags, attributes=allowed_attributes)

    return linkify(clean_html)

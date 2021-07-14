"""
Methods in this module are mostly direct copies from vespa.package.ApplicationPackage.
"""
from typing import List
from vespa.package import QueryProfile, QueryProfileType, Schema
from jinja2 import Environment, PackageLoader, select_autoescape
from datetime import datetime
from datetime import timedelta


def query_profile_to_text(query_profile: QueryProfile) -> str:
    env = Environment(
        loader=PackageLoader("vespa", "templates"),
        autoescape=select_autoescape(
            disabled_extensions=("txt",),
            default_for_string=True,
            default=True,
        ),
    )
    env.trim_blocks = True
    env.lstrip_blocks = True
    query_profile_template = env.get_template("query_profile.xml")
    return query_profile_template.render(fields=query_profile.fields)


def query_profile_type_to_text(query_profile_type: QueryProfileType) -> str:
    env = Environment(
        loader=PackageLoader("vespa", "templates"),
        autoescape=select_autoescape(
            disabled_extensions=("txt",),
            default_for_string=True,
            default=True,
        ),
    )
    env.trim_blocks = True
    env.lstrip_blocks = True
    query_profile_type_template = env.get_template("query_profile_type.xml")
    return query_profile_type_template.render(fields=query_profile_type.fields)


def hosts_to_text() -> str:
    env = Environment(
        loader=PackageLoader("vespa", "templates"),
        autoescape=select_autoescape(
            disabled_extensions=("txt",),
            default_for_string=True,
            default=True,
        ),
    )
    env.trim_blocks = True
    env.lstrip_blocks = True
    schema_template = env.get_template("hosts.xml")
    return schema_template.render()


def services_to_text(application_name: str, schemas: List[Schema]) -> str:
    env = Environment(
        loader=PackageLoader("vespa", "templates"),
        autoescape=select_autoescape(
            disabled_extensions=("txt",),
            default_for_string=True,
            default=True,
        ),
    )
    env.trim_blocks = True
    env.lstrip_blocks = True
    schema_template = env.get_template("services.xml")
    return schema_template.render(
        application_name=application_name,
        schemas=schemas,
    )


def validation_overrides_to_text() -> str:
    date = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
    return '<validation-overrides>\n\t<allow until="{}">content-type-removal</allow>\n</validation-overrides>'.format(
        date
    )

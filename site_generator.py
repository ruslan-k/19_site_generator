import json
import os
from distutils.dir_util import copy_tree

from jinja2 import Environment, PackageLoader
from markdown import markdown

CONFIG_FILE = 'config.json'

INDEX_TEMPLATE_FILENAME = 'index.html'
OUTPUT_INDEX_FILENAME = 'index.html'
ARTICLE_TEMPLATE_FILENAME = 'article.html'

INDEX_PAGE_TITLE = 'Энциклопедия'
SITE_NAME = 'My Site'

STATIC_FILES_FOLDER = 'static'
ARTICLES_FOLDER = 'articles'
OUTPUT_BASEDIR = 'output_site'
RENDERED_ARTICLES_FOLDER = 'encyclopedia'
TEMPLATES_FOLDER = 'templates'


def load_config_file():
    with open(CONFIG_FILE) as jsonfile:
        return json.loads(jsonfile.read())


def render_index_page_html(topics, articles, jinja_env):
    template = jinja_env.get_template(INDEX_TEMPLATE_FILENAME)
    context = {
        'title': INDEX_PAGE_TITLE,
        'site_name': SITE_NAME,
        'articles': articles,
        'topics': topics,
        'articles_folder': RENDERED_ARTICLES_FOLDER,
        'rel_path_to_static': STATIC_FILES_FOLDER,
        'rel_path_to_index': OUTPUT_INDEX_FILENAME
    }
    return template.render(context)


def convert_article_md_text_to_html(article_data):
    return markdown(
        os.path.join(ARTICLES_FOLDER, article_data['source'])
    )


def open_and_convert_md_text_to_html(path_to_md_file):
    with open(path_to_md_file) as md_file:
        return markdown(md_file.read())


def render_article_html(article_data, jinja_env):
    template = jinja_env.get_template(ARTICLE_TEMPLATE_FILENAME)
    path_to_md_file = os.path.join(
        ARTICLES_FOLDER,
        article_data['source']
    )
    article_html_content = open_and_convert_md_text_to_html(path_to_md_file)
    rel_path_to_root = "../../{}"
    context = {
        'title': article_data['title'],
        'article_html_content': article_html_content,
        'rel_path_to_static': rel_path_to_root.format(STATIC_FILES_FOLDER),
        'rel_path_to_index': rel_path_to_root.format(OUTPUT_INDEX_FILENAME)
    }
    return template.render(context)


def create_directories_for_rendered_files(path_to_output_file):
    os.makedirs(os.path.dirname(path_to_output_file), exist_ok=True)


def save_rendered_page(rendred_html, path_to_output_file):
    create_directories_for_rendered_files(path_to_output_file)
    with open(path_to_output_file, 'w+') as htmlfile:
        htmlfile.write(rendred_html)


def copy_static_files_to_output_folder():
    copy_tree(STATIC_FILES_FOLDER, "{}/{}".format(OUTPUT_BASEDIR, STATIC_FILES_FOLDER))


def generate_index_page_file(topics_data, articles_data, jinja_env):
    index_html = render_index_page_html(topics_data, articles_data, jinja_env)
    path_to_index_output_file = os.path.join(OUTPUT_BASEDIR, OUTPUT_INDEX_FILENAME)
    save_rendered_page(index_html, path_to_index_output_file)


def generate_articles_files(articles_data, jinja_env):
    for article_data in articles_data:
        article_html = render_article_html(article_data, jinja_env)
        path_to_article_output_file = os.path.join(OUTPUT_BASEDIR, RENDERED_ARTICLES_FOLDER,
                                                 article_data['source'].replace('.md', '.html'))
        save_rendered_page(article_html, path_to_article_output_file)


if __name__ == '__main__':
    jinja_env = Environment(loader=PackageLoader('site_generator', TEMPLATES_FOLDER))
    site_config = load_config_file()
    topics_data = site_config['topics']
    articles_data = site_config['articles']
    copy_static_files_to_output_folder()
    generate_index_page_file(topics_data, articles_data, jinja_env)
    generate_articles_files(articles_data, jinja_env)

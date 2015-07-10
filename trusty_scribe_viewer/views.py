from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import gitio
import sys

def index(request):
    return HttpResponseRedirect("/lab_notebook/")

def lab_notebook(request):
    N_commits = 50
    commit_list = []
    commit = gitio.get_head_commit()
    for i in range(N_commits):
        prev_commit = commit.prev
        message_lines = commit.message.splitlines()
        title = message_lines[0]
        body = "\n".join(message_lines[1:])
        commit_list.append({'title'         : title,
                            'commit_id'     : commit.sha,
                            'timestamp'     : commit.timestamp,
                            'prev_commit_id': prev_commit.sha,
                            'body'          : body})
        commit = prev_commit
    return HttpResponse(render_lab_notebook(gitio.repo_name, commit_list))

def render_lab_notebook(repo_name, entries):
    contents = "".join([notebook_entry_template.format(**kwargs)
                        for kwargs in entries])
    title = notebook_template.format(repo_name=repo_name)
    return title + contents

notebook_template = """\
<!doctype html>
<title>Lab Notebook</title>
<h1>Lab Notebook for {repo_name}:</h1>
"""
notebook_entry_template = """\
<h3>{timestamp} : {title}</h3>
<p>
  <a href="/browse/{commit_id}/">Browse</a>
  <a href="/diffs/{prev_commit_id}/{commit_id}/">Diff</a>
</p>
<p>{body}</p>
"""

def browse(request, path_string):
    commit_id_and_path = filter(bool, path_string.split('/'))
    commit_id, path = commit_id_and_path[0], commit_id_and_path[1:]
    commit = gitio.Commit(commit_id)
    obj, obj_type = commit.obj_from_path(path)
    if obj_type == 'directory':
        if path_string[-1] == '/':
            return HttpResponse(render_directory(obj, commit_id, path))
        else:
            url_with_trailing_slash = "/browse/{0}/".format(path_string)
            return HttpResponseRedirect(url_with_trailing_slash)
    elif obj_type == 'file':
        return HttpResponse(obj, content_type='text/plain')
    else:
        raise Exception

def render_directory(children, commit_id, path):
    dirname = "/".join(path)
    children += [".."]
    contents = "".join(map(dir_entry_template.format, children))
    return dir_template.format(dirname=dirname,
                               commit_id=commit_id[:10],
                               contents=contents)

dir_template = """\
<!doctype html>
<title>Directory {dirname}</title>
<h2>Contents of directory {dirname} at commit {commit_id}:</h2>
<ul>{contents}</ul>
"""
dir_entry_template = """\
<li><a href="{0}">{0}</a></li>
"""

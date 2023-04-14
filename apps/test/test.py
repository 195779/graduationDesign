import base64
import os

from flask import Flask, request, make_response, redirect, render_template, url_for, flash, session, abort
from apps.test.__init__ import test_bp


@test_bp.route('/')
def index():
    return render_template('test/base.html', page='page_index')


@test_bp.route('/page1')
def page1():
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 处理异步请求的逻辑
        return render_template('test/center.html', page="page1")
    else:
        # 处理非异步请求的逻辑
        return render_template('test/base.html', page='page1')


@test_bp.route('/page2')
def page2():
    return render_template('test/center.html', page="page2")


@test_bp.route('/page3')
def page3():
    return render_template('test/center.html', page='page3')
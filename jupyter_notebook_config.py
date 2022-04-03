# Configuration file for ipython-notebook.
import os

c = get_config()
c.NotebookApp.ip = '0.0.0.0'
c.NotebookApp.open_browser = False
c.NotebookApp.port = 8888

c.NotebookApp.log_format = '[%(name)s] %(message)s'
c.NotebookApp.log_level = 30

c.NotebookApp.notebook_dir = '/notebooks'

c.NotebookApp.password = u'sha1:41577da769c5:122daef65ef7aef9776261f4bfc0b4f1d804d445'
c.NotebookApp.shutdown_no_activity_timeout = 1800

c.NotebookApp.allow_origin = os.environ.get("ALLOW_ORIGIN")

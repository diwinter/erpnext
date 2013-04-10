import webnotes, webnotes.utils, os
from webnotes.modules.export_file import export_to_files

def execute():
	webnotes.reload_doc("core", "doctype", "file_data")
	webontes.reset_perms("File Data")
	
	singles = webnotes.conn.sql_list("""select name from tabDocType
		where ifnull(issingle,0)=1""")
	for doctype in webnotes.conn.sql_list("""select parent from tabDocField where 
		fieldname='file_list' and fieldtype='Text'"""):
		if doctype in singles:
			doc = webnotes.doc(doctype, doctype)
			update_for_doc(doctype, doc)
			webnotes.conn.set_value(doctype, None, "file_list", None)
		else:
			try:
				for doc in webnotes.conn.sql("""select name, file_list from `tab%s` where 
					ifnull(file_list, '')!=''""" % doctype, as_dict=True):
					update_for_doc(doctype, doc)
				webnotes.conn.commit()
				webnotes.conn.sql("""alter table `tab%s` drop column file_list""" % doctype)
			except Exception, e:
				if e.args[0]!=1054: raise e
		
		webnotes.conn.sql("""delete from tabDocField where fieldname='file_list'
				and parent=%s""", doctype)
		export_to_files([["DocType", doctype]])

def update_for_doc(doctype, doc):
	for filedata in doc.file_list.split("\n"):
		if not filedata:
			continue
			
		filename, fileid = filedata.split(",")
		
		exists = True
		if not (filename.startswith("http://") or filename.startswith("https://")):
			if not os.path.exists(webnotes.utils.get_path("public", "files", filename)):
				exists = False

		if exists:
			webnotes.conn.sql("""update `tabFile Data` 
				set attached_to_doctype=%s, attached_to_name=%s
				where name=%s""", (doctype, doc.name, fileid))
		
		else:
			webnotes.conn.sql("""delete from `tabFile Data` where name=%s""",
				fileid)	
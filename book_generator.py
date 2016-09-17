import os
from fnmatch import fnmatch

_default_ignore_files = ['.*','__*', '*.h', '*.hpp', '*.vcxproj*', '*.sln', "Clean", "*akefile*"]
_default_ignore_dirs = ['.*', '__*']
_ext2lang = {
    'py': 'Python',
    'cpp': 'C++',
    'c': 'C',
    'h': 'C'
}
_depth2section = {
    0: 'part',
    1: 'chapter',   
    2: 'section',
    3: 'subsection'
}

class Book:
    def __init__(self, output_file_path='book.tex', titles=["Some book"], authors=["Jane Doe"]):
        self._output_file_path = output_file_path
        self._titles = titles
        self._authors = authors
        self._depth = 0
        self._file = None

    def __enter__(self):
        self._file = open(self._output_file_path, mode='w+')
        self._make_heading()
        return self
        
    def __exit__(self, etye, eval, traceback):
        self._file.write('\end{document}')
        self._file.close()
    
    def _make_heading(self):
        with open('_settings.tex') as s:
            self._file.writelines(s.readlines())
            self._file.write('\n')
            titles = " \\\\ ".join(self._titles)
            authors = " \\\\ ".join(self._authors)
            heading = [
                "\\title{{{titles}}}".format(titles=titles),
                "\\author{{{authors}}}".format(authors=authors),
                "\\begin{document}",
                "\\maketitle",
                "\\tableofcontents",
            ]
            self._file.writelines("\n".join(heading)+"\n")

    def _get_path_name_lang(self, file_path):
        file_name = file_path.split(os.sep)[-1]
        if '.' not in file_name:
            file_path = file_path + '.'
        try:
            name, ext = file_name.split('.')
        except ValueError:
            ext = ""
        lang = _ext2lang.get(ext, "C")
        if "Makefile" in file_name:
            lang = "Make"
        return file_path, file_name, lang

    def add_listing(self, file_path, depth):
        file_path, file_name, lang = self._get_path_name_lang(file_path)
        self._write_chapter(self._depth+1, file_name)
        set_lang = '\lstset{{language={lang}}}'.format(lang=lang)
        list_file = '\lstinputlisting{{{file_path}}}'.format(file_path=file_path)
        
        listing = '\n'.join(['', set_lang, list_file])+'\n' #\\newpage
        self._file.writelines(listing)
        
    def add_chapter(self, name, depth):
        self._depth = depth
        self._write_chapter(depth, name)

    def _write_chapter(self, depth, name):
        name = name.replace("__","").replace("_", " ")
        if not name:
            return
        section = _depth2section.get(depth, 'subsection')
        self._file.write("\{section}{{{name}}}\n".format(section=section, name=name))


class BookGenerator:
    def __init__(self, path, ignore_files=_default_ignore_files, 
                 ignore_dirs=_default_ignore_dirs, output='book.tex'):
        self._repo_path = path
        self._ignore_files = ignore_files
        self._ignore_dirs = ignore_dirs
    
    def run(self):
        with Book(titles=['SGS', 'Social Game Server'], authors=["Marcin Meinardi", "with Ganymede folks"]) as book:
            for path, dirs, files in os.walk(self._repo_path):
                dir_path = path.replace(self._repo_path, '')
                if self.skip_dir(dir_path):
                    continue

                print('Processing {0}'.format(path))
                depth = dir_path.count(os.sep)
                if depth > 0:
                    book.add_chapter(path.split(os.sep)[-1], depth)
            
                for f in files:
                    if self.skip_file(f):
                        continue
                    file_path = os.path.join(path, f)
                    print("Processing {0} {1}".format(" "*depth*2, file_path))
                    book.add_listing(file_path, depth)
    
    def skip_file(self, file):
        return any(fnmatch(file, pattern) for pattern in self._ignore_files)

    def skip_dir(self, dir_path):
        dirs = dir_path.split(os.sep)
        for d in dirs:
            if any(fnmatch(d, pattern) for pattern in self._ignore_dirs):
                return True
        return False

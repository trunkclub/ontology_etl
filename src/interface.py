#!/usr/bin/env python
"""
Taken from a test file included in the npyscreen repository.
"""

import npyscreen
import yaml

class TreeForm(npyscreen.ActionForm):
    def create(self):

        d = yaml.load(
            open('/home/vagrant/trunk/ontology_etl/configs/entities/entities.yaml', 'r'))
        wgtree = self.add(MyTree)
        wgtree.values = wgtree.make_tree(tree_dict=d)
        # tree_data = self.make_tree(tree_dict=d)
        # self.values = tree_data


class MyTree(npyscreen.MLTreeAction):
    def __init__(self, *args, **kwargs):
        super(MyTree, self).__init__(*args, **kwargs)

    def make_tree(self, parent=None, tree_dict=None, root_content='root'):
        root = parent or npyscreen.TreeData(
            content=root_content, selectable=True, ignore_root=False) 
        parent = parent or root
        if not isinstance(tree_dict, dict):
            return root
        for key, value in tree_dict.iteritems():
            if isinstance(value, dict):
                new_node = parent.new_child(content=key)
                self.make_tree(parent=new_node, tree_dict=value)
            elif isinstance(value, list):
                new_node = parent.new_child(content=key)
                for element in value:
                    self.make_tree(parent=new_node, tree_dict=element)
            else:
                new_node = parent.new_child(content=key)
        return root
    

class TestDictApp(npyscreen.NPSAppManaged):
    def onStart(self):
        my_tree_form = TreeForm()
        self.registerForm("MAIN", my_tree_form)
        my_tree_form.edit()  # ?
        


if __name__ == "__main__":
    d = {
        'foo': 'bar',
        'bar': 'baz',
        'qux': {'goo': 'foobar', 'foobar': {'fooagain': 'anotherqux'}},
        'abc': [{'xyz': 'fgh'}, {'def': '123'}]}

    d = yaml.load(open('/home/vagrant/trunk/ontology_etl/configs/entities/entities.yaml', 'r'))
    App = TestDictApp()
    App.run()   

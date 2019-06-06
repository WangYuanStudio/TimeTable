from PyQt5.QtWidgets import QApplication, QWidget
from ui import Ui_widget
import sys
import os
import datetime
import webbrowser


class Win(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_widget()
        self.ui.setupUi(self)

        self.data = {}
        self.table = {}

        self.ui.btn_add.clicked.connect(self.add)
        self.ui.btn_remove.clicked.connect(self.remove)
        self.ui.btn_generate.clicked.connect(self.generate)
        self.ui.list_person.currentRowChanged.connect(self.change)
        for col in ['a', 'b']:
            for row in range(1, 6):
                lab = 'btn_' + col + str(row)
                if hasattr(self.ui, lab):
                    obj = getattr(self.ui, lab)
                    obj.clicked.connect(self.select)

        self.ui.box_select.setEnabled(False)
        self.ui.line_edit.setFocus()

        self.load()

    def add(self):
        name = self.ui.line_edit.text()
        if name is '':
            return

        for i in range(self.ui.list_person.count()):
            if self.ui.list_person.item(i).text() == name:
                return

        self.ui.list_person.addItem(name)
        self.ui.line_edit.setText('')

        self.data[name] = {}
        for col in ['a', 'b']:
            for row in range(1, 6):
                lab = col + str(row)
                self.data[name][lab] = False

        self.ui.list_person.setCurrentRow(self.ui.list_person.count() - 1)
        self.change()
        self.save()

    def remove(self):
        if self.ui.list_person.currentRow() != -1:
            name = self.ui.list_person.currentItem().text()
            del self.data[name]
            self.ui.list_person.takeItem(self.ui.list_person.currentRow())

            self.change()
            self.save()

    def generate(self):
        data_set = {}
        person_times = {}
        person_has_times = {}

        for name in self.data:
            person_times[name] = 0
            person_has_times[name] = 0

            for key in self.data[name]:
                if not self.data[name][key]:
                    continue

                person_times[name] += 1

                if key not in data_set:
                    data_set[key] = [name]
                else:
                    data_set[key].append(name)

        data_origin = data_set.copy()
        data_select = {}

        for col in ['a', 'b']:
            for row in range(1, 6):
                lab = col + str(row)
                data_select[lab] = []

                if lab in data_set:
                    if 0 < len(data_set[lab]) <= 3:
                        data_select[lab] += data_set[lab]
                        for name in data_set[lab]:
                            person_has_times[name] += 1

                        del data_set[lab]

        for person in person_times:
            if person_times[person] <= self.ui.limit_times.value():
                for lab in data_set:
                    for name in data_set[lab]:
                        if name == person:
                            if lab in data_select:
                                if name not in data_select[lab]:
                                    data_select[lab].append(name)
                                    person_has_times[name] += 1
                            else:
                                data_select[lab] = [name]
                                person_has_times[name] += 1

                            data_set[lab].remove(name)

        for person in person_has_times:
            if person_has_times[person] < self.ui.limit_times.value():
                while self.ui.limit_times.value() - person_has_times[person]:
                    min_lab = None
                    min_count = 100
                    for col in ['a', 'b']:
                        for row in range(1, 6):
                            lab = col + str(row)

                            if not self.data[person][lab] or lab not in data_set or person not in data_set[lab]:
                                continue

                            if lab not in data_select:
                                min_lab = lab
                                min_count = 0
                                break
                            elif len(data_select[lab]) < min_count:
                                min_lab = lab
                                min_count = len(data_select[lab])

                    person_has_times[person] += 1
                    if min_lab:
                        if min_lab not in data_select:
                            data_select[min_lab] = person
                        else:
                            data_select[min_lab].append(person)

                        data_set[min_lab].remove(person)

        # 分离 黎灿 和行政楼
        data_207 = {}
        data_308 = {}

        for lab in data_select:
            if len(lab) == 1:
                data_207[lab] = lab
                del data_select[lab]

        for person in person_has_times:
            min_lab = None
            min_count = 100
            for col in ['a', 'b']:
                for row in range(1, 6):
                    lab = col + str(row)

                    if lab not in data_select or person not in data_select[lab]:
                        continue

                    if len(data_select[lab]) < min_count:
                        if lab not in data_207 or len(data_207[lab]) < 2:
                            min_lab = lab
                            min_count = len(data_select[lab])

            if min_lab:
                if min_lab not in data_207:
                    data_207[min_lab] = [person]
                else:
                    data_207[min_lab].append(person)

                data_select[min_lab].remove(person)

        for col in ['a', 'b']:
            for row in range(1, 6):
                lab = col + str(row)

                if lab not in data_207 or len(data_207[lab]) != 2:
                    if lab in data_set and data_set[lab]:

                        for person in data_set[lab]:
                            exits = False

                            for lab_t in data_207:
                                if person in data_207[lab_t]:
                                    exits = True
                                    break

                            if not exits:
                                max_lab = None
                                max_count = 0
                                for lab_t in data_select:
                                    if len(data_select[lab_t]) > max_count and person in data_select[lab_t]:
                                        max_count = len(data_select[lab_t])
                                        max_lab = lab_t

                                if max_lab:
                                    if lab in data_207:
                                        data_207[lab].append(person)
                                    else:
                                        data_207[lab] = [person]

                                    data_select[max_lab].remove(person)
                                    data_set[lab].remove(person)
                                    break

        for col in ['a', 'b']:
            for row in range(1, 6):
                lab = col + str(row)
                while lab not in data_207 or len(data_207[lab]) < 2:
                    if lab not in data_select:
                        break

                    if data_select[lab] == 1 and len(data_207[lab]) == 1:
                        break

                    min_207_times = 10
                    max_times = 0
                    max_person = None
                    for person in data_select[lab]:
                        times = 0
                        for lab_t in data_207:
                            if person in data_207[lab_t]:
                                times += 1

                        max_person_times = person_times[person]

                        if times <= min_207_times and max_person_times >= max_times:
                            min_207_times = times
                            max_times = max_person_times
                            max_person = person

                    if max_person:
                        if lab not in data_207:
                            data_207[lab] = [max_person]
                        else:
                            data_207[lab].append(max_person)

                        data_select[lab].remove(max_person)

        data_308 = data_select

        print('data-origin:\t', data_origin)
        print('data-207:\t', data_207)
        print('data-308:\t', data_308)
        print('data-set:\t', data_set)

        tr_text = ""
        for col in ['a', 'b']:
            td_text = ""
            for row in range(1, 6):
                item_207 = ""
                item_308 = ""
                item_other = ""

                lab = col + str(row)
                if lab in data_207:
                    for person in data_207[lab]:
                        item_207 += "<div style='color:red'>" + person + "</div>"

                if lab in data_308:
                    for person in data_308[lab]:
                        item_308 += "<div style='color:green'>" + person + "</div>"

                if lab in data_set:
                    for person in data_set[lab]:
                        item_other += "<div style='color:#444'>" + person + "</div>"

                td_text += "<td>" + item_207 + item_308 + item_other + "</td>"

            tr_title = '56 节' if col == 'a' else '78 节'
            tr_text += "<tr><th>" + tr_title + "</th>" + td_text + "</tr>"

        html = "<html>" \
               "<head><title>网园值班表</title><meta charset='utf-8'>" \
               "<style type='text/css'>" \
               "th {background-color:rgba(0,0,0,0.1); min-width:104px; padding: 8px}" \
               "td {background-color:rgba(0,0,0,0.05); min-width:104px; text-align:center; padding: 16px; vertical-align: top}" \
               "</style>" \
               "</head>" \
               "<body><div style='margin: 80px auto; text-align: center;'>" \
               "<h1>网园资讯工作室值班表</h1>" \
               "<table style='border:1px solid #aaa; margin:0 auto'>" \
               "<tr><th></th><th>周一</th><th>周二</th><th>周三</th><th>周四</th><th>周五</th></tr>" \
               + tr_text + \
               "</table>" \
               "<br><div style='width:960px; margin: 0 auto; text-align:left'><hr>" \
               "<span style='margin-left: 20px; background-color:red; width:20px; height:20px;display:inline-block;'></span>行政楼 207" \
               "<span style='margin-left: 20px; background-color:green; width:20px; height:20px;display:inline-block;'></span>黎灿 308" \
               "<span style='margin-left: 20px; background-color:#444; width:20px; height:20px;display:inline-block;'></span>未安排" \
               "<span style='float:right'>" + str(datetime.datetime.date(datetime.datetime.now())) + "</span>" \
               "</div></div></body></html>"

        with open('./timetable.html', 'w') as fp:
            fp.write(html)

        if os.path.exists('./timetable.html'):
            file = os.path.abspath('./timetable.html')
            webbrowser.open(file)

    def change(self):
        if self.ui.list_person.currentRow() != -1:
            self.ui.btn_remove.setEnabled(True)
            self.ui.box_select.setEnabled(True)

            name = self.ui.list_person.currentItem().text()
            for col in ['a', 'b']:
                for row in range(1, 6):
                    lab = col + str(row)
                    if hasattr(self.ui, 'btn_' + lab):
                        obj = getattr(self.ui, 'btn_' + lab)
                        obj.setChecked(self.data[name][lab])

        else:
            self.ui.btn_remove.setEnabled(False)
            self.ui.box_select.setEnabled(False)

            for col in ['a', 'b']:
                for row in range(1, 6):
                    lab = 'btn_' + col + str(row)
                    if hasattr(self.ui, lab):
                        obj = getattr(self.ui, lab)
                        obj.setChecked(False)

        if self.ui.list_person.count() == 0:
            self.ui.btn_generate.setEnabled(False)
        else:
            self.ui.btn_generate.setEnabled(True)

    def select(self):
        sender = self.sender()
        name = self.ui.list_person.currentItem().text()
        lab = sender.objectName()[-2:]
        self.data[name][lab] = sender.isChecked()

        self.save()

    def save(self):
        with open('./timetable.json', 'w') as fp:
            fp.write(str(self.data))

    def load(self):
        if os.path.exists('./timetable.json'):
            with open('./timetable.json', 'r') as fp:
                try:
                    self.data = eval(fp.read())
                except:
                    print('load file error!')

        if self.data is not None:
            for key in self.data:
                self.ui.list_person.addItem(key)

            if self.ui.list_person.count() > 0:
                self.ui.list_person.setCurrentRow(0)
                self.change()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Win()
    win.show()
    sys.exit(app.exec_())


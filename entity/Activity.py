'''
@author: Ethan

@description:

@website:http://www.guohe3.com

@contact: pxc2955317305@gmail.com

@time: 2018/4/20 14:40

'''


class Activity(object):
    def __init__(self,id, name, detail, imgs, start_time, end_time, organizer, contact, place, note, type):
        self.id=id
        self.name = name
        self.detail = detail
        self.imgs = imgs
        self.start_time = start_time
        self.end_time = end_time
        self.organizer = organizer
        self.contact = contact
        self.place = place
        self.note = note
        self.type = type

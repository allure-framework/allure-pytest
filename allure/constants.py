'''
Various constants extracted from schema.

Created on Oct 15, 2013

@author: pupssman
'''
from enum import Enum


class Status:
    FAILED = 'failed'
    BROKEN = 'broken'
    PASSED = 'passed'
    SKIPPED = 'canceled'
    CANCELED = 'canceled'
    PENDING = 'pending'


class Label:
    DEFAULT = 'allure_label'
    FEATURE = 'feature'
    STORY = 'story'
    SEVERITY = 'severity'
    ISSUE = 'issue'


class Severity:
    BLOCKER = 'blocker'
    CRITICAL = 'critical'
    NORMAL = 'normal'
    MINOR = 'minor'
    TRIVIAL = 'trivial'


class AttachmentType(Enum):
    def __init__(self, mime_type, extension):
        self.mime_type = mime_type
        self.extension = extension

    TEXT = ("text/plain", "txt")
    HTML = ("application/html", "html")
    XML = ("application/xml", "xml")
    PNG = ("image/png", "png")
    JPG = ("image/jpg", "jpg")
    JSON = ("application/json", "json")
    OTHER = ("other", "other")


ALLURE_NAMESPACE = "urn:model.allure.qatools.yandex.ru"
FAILED_STATUSES = [Status.FAILED, Status.BROKEN]

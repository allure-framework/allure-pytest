'''
Various constants extracted from schema.

Created on Oct 15, 2013

@author: pupssman
'''


class Severity:
    BLOCKER = 'blocker'
    CRITICAL = 'critical'
    NORMAL = 'normal'
    MINOR = 'minor'
    TRIVIAL = 'trivial'


class Status:
    FAILED = 'failed'
    BROKEN = 'broken'
    PASSED = 'passed'
    SKIPPED = 'skipped'


FAILED_STATUSES = [Status.FAILED, Status.BROKEN]


class AttachmentType:
    TEXT = "txt"
    HTML = "html"
    XML = "xml"
    PNG = "png"
    JPG = "jpg"
    JSON = "json"
    OTHER = "other"


ALLURE_NAMESPACE = "urn:model.allure.qatools.yandex.ru"


class Label:
    DEFAULT = 'allure_label'
    FEATURE = 'feature'
    STORY = 'story'

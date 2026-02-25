"""Pydantic 스키마"""
from .common import APIResponse, PaginatedResponse
from .academy import AcademyBase, AcademyCreate, AcademyUpdate, AcademyResponse
from .teacher import TeacherBase, TeacherCreate, TeacherUpdate, TeacherResponse
from .subject import SubjectBase, SubjectCreate, SubjectUpdate, SubjectResponse
from .collection_source import CollectionSourceBase, CollectionSourceCreate, CollectionSourceResponse

import logging
logger = logging.getLogger(__name__)

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test import Client

from mezzanine.blog.models import BlogCategory
from mezzanine.pages.models import RichTextPage

from website.jdpages.models import ColumnElement
from website.jdpages.models import Sidebar
from website.jdpages.views import BlogCategorySidebarItem
from website.jdpages.views import TwitterSidebarItem
from website.jdpages.views import TabsSidebarItem
from website.jdpages.views import SocialMediaButtonGroupItem


class TestCaseAdminLogin(TestCase):
    """ Test case with client and login as admin function. """

    def setUp(self):
        # Needed during tests with DEBUG=False (the default)
        # to prevent a TemplateDoesNotExist error of a filebrowser template.
        # Not sure what goes wrong here, but seems to work fine in manual tests.
        settings.TEMPLATE_DEBUG = False
        self.client = Client()
        self.login()

    def login(self):
        """ Login as admin. """
        response = self.client.post('/admin/login/?next=/admin/', {'username': 'admin', 'password': 'admin'}, follow=True)
        self.assertEqual(response.status_code, 200)
        return response


class TestColumnElement(TestCase):
    """ ColumnElement test case. """

    def test_auto_create(self):
        """
        Tests whether a ColumnElement is automatically created
        when a BlogCategory is created, and that the element contains a reference to the category object.
        """
        category = BlogCategory.objects.create(title="Test Blog")
        content_type = ContentType.objects.get(model="blogcategory")
        element = ColumnElement.objects.get(object_id=category.id, content_type=content_type)
        self.assertEqual(element.get_object(), category)

    def test_auto_delete(self):
        """
        Tests whether a ColumnElement is automatically deleted
        when a BlogCategory is deleted.
        """
        category = BlogCategory.objects.create(title="Test Blog")
        content_type = ContentType.objects.get(model="blogcategory")
        element = ColumnElement.objects.get(object_id=category.id, content_type=content_type)
        self.assertEqual(element.get_object(), category)
        catid = category.id
        category.delete()
        self.assertEqual(BlogCategory.objects.count(), 0)
        self.assertEqual(ColumnElement.objects.filter(object_id=catid, content_type=content_type).exists(), False)


class TestSidebar(TestCaseAdminLogin):
    """ Tests the sidebar and its widgets. """
    fixtures = ['test_sidebar.json']

    def test_edit_sidebar_admin_view(self):
        """ Tests whether the change sidebar admin view response is OK (200). """
        sidebars = Sidebar.objects.all()
        self.assertEquals(sidebars.count(), 1)
        sidebar = sidebars[0]
        response = self.client.get('/admin/jdpages/sidebar/' + str(sidebar.id) + '/', follow=True)
        self.assertEqual(response.status_code, 200)

    def test_view_items_sidebar(self):
        """ Tests whether the sidebar view items exist in the homepage context. """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        items = response.context['sidebar_items']
        self.assertTrue(type(items[0]) == BlogCategorySidebarItem)
        self.assertTrue(type(items[1]) == TabsSidebarItem)
        self.assertTrue(type(items[2]) == TwitterSidebarItem)
        self.assertTrue(type(items[3]) == SocialMediaButtonGroupItem)


class TestPage(TestCaseAdminLogin):
    """ Tests the basic page structure and admin. """
    fixtures = ['test_pages.json']

    def test_edit_richtextpage_admin_view(self):
        richtextpages = RichTextPage.objects.all()
        self.assertEqual(len(richtextpages), 6)
        for page in richtextpages:
            response = self.client.get('/admin/pages/richtextpage/' + str(page.id) + '/', follow=False)
            self.assertEqual(response.status_code, 200)

    def test_richtextpage_view(self):
        richtextpages = RichTextPage.objects.all()
        for page in richtextpages:
            response = self.client.get(page.get_absolute_url(), follow=True)
            self.assertEqual(response.status_code, 200)


class TestPageHeaderImage(TestCaseAdminLogin):
    """ Tests the header image of pages. """
    fixtures = ['test_pages.json']

    def test_edit_header_admin_view(self):
        richtextpages = RichTextPage.objects.all()
        for page in richtextpages:
            response = self.client.get('/admin/pages/richtextpage/' + str(page.id) + '/', follow=True)
            self.assertEqual(response.status_code, 200)

    def test_header_page_view(self):
        richtextpages = RichTextPage.objects.all()
        for page in richtextpages:
            response = self.client.get(page.get_absolute_url(), follow=True)
            self.assertEqual(response.status_code, 200)
            page_header_image_wiget = response.context['page_header']
            if page.id == 4:
                self.assertEqual(page_header_image_wiget.page.id, 2)
                self.assertEqual(str(page_header_image_wiget.image), 'uploads/site-1/example_header.jpg')
            if page.id == 7:
                self.assertEqual(page_header_image_wiget, None)
            if page.id == 3:
                self.assertEqual(page_header_image_wiget.page.id, 2)
                self.assertEqual(str(page_header_image_wiget.image), 'uploads/site-1/example_header.jpg')
            if page.id == 5:
                self.assertEqual(page_header_image_wiget, None)
            if page.id == 6:
                self.assertEqual(page_header_image_wiget, None)
            if page.id == 8:
                self.assertEqual(page_header_image_wiget.page.id, 8)
                self.assertEqual(str(page_header_image_wiget.image), 'uploads/site-1/example_header_subpage.jpg')

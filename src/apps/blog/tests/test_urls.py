from django.urls import resolve, reverse


def test_list():
    assert reverse("blog:list") == "/blog/"
    assert resolve("/blog/").view_name == "blog:list"


def test_detail():
    assert reverse("blog:detail", kwargs={"slug": "test"}) == "/blog/test/"
    assert resolve("/blog/test/").view_name == "blog:detail"


def test_delete_comment():
    assert reverse("blog:comment_delete", kwargs={"pk": 2}) == "/blog/comment/delete/2/"
    assert resolve("/blog/comment/delete/2/").view_name == "blog:comment_delete"

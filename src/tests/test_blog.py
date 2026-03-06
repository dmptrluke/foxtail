import pytest
from faker import Faker
from selenium.webdriver.common.by import By

from apps.blog.models import Post

fake = Faker()
pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_blog_comments(authenticated_driver, user, live_server, post: Post):
    driver = authenticated_driver

    # user heads to the contact page
    driver.get(live_server.url + post.get_absolute_url())

    # the title contains the website name
    assert 'example.com' in driver.title

    # the comments section is visible with a form
    comment_section = driver.find_element(By.CLASS_NAME, 'comments-section')
    comment_form = comment_section.find_element(By.CLASS_NAME, 'comment-form')

    # no comments yet
    comments = comment_section.find_elements(By.CLASS_NAME, 'comment-item')
    assert len(comments) == 0

    # lets make a comment!
    comment_text = fake.sentence()

    comment_field = comment_form.find_element(By.NAME, 'text')
    comment_field.send_keys(comment_text)

    comment_form.find_element(By.NAME, 'post-comment').click()

    # the user sees a green alert
    alert = driver.find_element(By.CLASS_NAME, 'alert-success')
    assert 'Your comment has been posted!' in alert.text

    # we read the comments again
    comment_section = driver.find_element(By.CLASS_NAME, 'comments-section')
    comments = comment_section.find_elements(By.CLASS_NAME, 'comment-item')

    assert len(comments) == 1

    my_comment = comments[0]

    # we make sure the comment is all good
    assert user.get_short_name() in my_comment.text
    assert comment_text in my_comment.text

    # we don't like it, delete it!
    delete_link = my_comment.find_element(By.LINK_TEXT, 'delete')
    delete_link.click()

    # we see the deletion page...
    body = driver.find_element(By.ID, 'main-content')
    assert 'sure you want to delete' in body.text
    assert comment_text in body.text

    # ...and hit delete
    delete_button = body.find_element(By.CSS_SELECTOR, 'button.btn-danger')
    delete_button.click()

    # we should now be back at the post page
    assert driver.current_url == live_server.url + post.get_absolute_url()

    # the comment is gone
    comment_section = driver.find_element(By.CLASS_NAME, 'comments-section')
    comments = comment_section.find_elements(By.CLASS_NAME, 'comment-item')

    # now there are none
    assert len(comments) == 0

    # we make sure the comment is not here
    assert comment_text not in comment_section.text

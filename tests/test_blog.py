import pytest
from faker import Faker
from selenium.webdriver.common.by import By

from foxtail_blog.models import Post

fake = Faker()
pytestmark = pytest.mark.django_db


@pytest.mark.django_db
def test_blog_comments(authenticated_driver, user, live_server, post: Post):
    driver = authenticated_driver

    # user heads to the contact page
    driver.get(live_server.url + post.get_absolute_url())

    # the title contains the website name
    assert 'example.com' in driver.title

    # get some things!
    comment_area = driver.find_element(By.ID, 'comments')
    comment_form = driver.find_element(By.ID, 'comments-form')

    # there is already a comment
    comments = comment_area.find_element(By.CLASS_NAME, 'comment')

    # only one
    assert len(comments) == 0

    # lets make a comment!
    comment_text = fake.sentence()

    comment_field = comment_form.find_element(By.NAME, 'text')
    comment_field.send_keys(comment_text)

    comment_form.find_element(By.NAME, 'post-comment').click()

    # the user sees a green alert
    alert = driver.find_element(By.CLASS_NAME, 'alert-success')
    assert "Your comment has been posted!" in alert.text

    # we read the comments again
    comment_area = driver.find_element(By.ID, 'comments')
    comments = comment_area.find_element(By.CLASS_NAME, 'comment')

    assert len(comments) == 1

    my_comment = comments[0]

    # we make sure the comment is all good
    assert user.username in my_comment.text
    assert comment_text in my_comment.text

    # we don't like it, delete it!
    delete_button = my_comment.find_element(By.LINK_TEXT, 'delete comment')
    delete_button.click()

    # we see the deletion page...
    body = driver.find_element(By.ID, 'main-content')
    assert 'sure you want to delete' in body.text
    assert comment_text in body.text

    # ...and hit delete
    delete_button = driver.find_element(By.ID, 'delete-button')
    delete_button.click()

    # we should now be back at the post page
    assert driver.current_url == live_server.url + post.get_absolute_url()

    # the comment is gone
    comment_area = driver.find_element(By.ID, 'comments')
    comments = comment_area.find_element(By.CLASS_NAME, 'comment')

    # now there are none
    assert len(comments) == 0

    # we make sure the comment is not here
    assert comment_text not in comment_area.text

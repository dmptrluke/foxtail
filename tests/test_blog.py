import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_blog_comments(authenticated_driver, live_server, settings):
    settings.RECAPTCHA_ENABLED = False

    driver = authenticated_driver

    # user heads to the contact page
    driver.get(live_server.url + reverse('blog_detail', kwargs={'slug': 'test-one'}))

    # the title contains the website name
    assert 'furry.nz' in driver.title

    # get some things!
    comment_area = driver.find_element_by_id('comments')
    comment_form = driver.find_element_by_id('comments-form')

    # there is already a comment
    comments = comment_area.find_elements_by_class_name('comment')

    # only one
    assert len(comments) == 1

    # lets make a comment!
    comment_field = comment_form.find_element_by_name('text')
    comment_field.send_keys('I like this post')

    comment_form.find_element_by_name('submit').click()

    # the user sees a green alert
    alert = driver.find_element_by_class_name('alert-success')
    assert "Your comment has been posted!" in alert.text

    # we read the comments again
    comment_area = driver.find_element_by_id('comments')
    comments = comment_area.find_elements_by_class_name('comment')

    # now there are two!
    assert len(comments) == 2

    their_comment = comments[0]
    my_comment = comments[1]

    # we make sure the comment is all good
    assert 'test' in my_comment.text
    assert 'I like this post' in my_comment.text

    assert 'Hello' in their_comment.text

    # we don't like it, delete it!
    delete_button = my_comment.find_element_by_link_text('delete comment')
    delete_button.click()

    # we see the deletion page...
    body = driver.find_element_by_id('main-content')
    assert 'sure you want to delete' in body.text
    assert 'I like this post' in body.text

    # ...and hit delete
    delete_button = driver.find_element_by_id('delete-button')
    delete_button.click()

    # we should now be back at the post page
    assert driver.current_url == live_server.url + reverse('blog_detail', kwargs={'slug': 'test-one'})

    # the comment is gone
    comment_area = driver.find_element_by_id('comments')
    comments = comment_area.find_elements_by_class_name('comment')

    # now there is only one :(
    assert len(comments) == 1

    # we make sure the comment is not here
    assert 'I like this post' not in comment_area.text

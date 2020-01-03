from datetime import datetime

import pytest

from foxtail_blog.models import Post

pytestmark = pytest.mark.django_db


def test_unauthenticated_user_browsing(driver, live_server, settings, post: Post, second_post: Post):
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

    post.created = datetime(2019, 12, 2)
    second_post.created = datetime(2019, 11, 1)

    post.save()
    second_post.save()

    # user visits the website
    driver.get(live_server.url)

    # the title contains the website name
    assert 'example.com' in driver.title

    # user sees the sign in button
    sign_in_button = driver.find_element_by_link_text("Sign In")
    assert sign_in_button

    # user sees the blog posts on the homepage, and reads the content
    blog_cards = driver.find_element_by_id('blog-cards').find_elements_by_class_name('index-card')

    # there are two blog postss
    assert len(blog_cards) == 2

    # the user reads the blog post title, and some of the text
    card_one = blog_cards[0]
    assert post.title in card_one.text
    assert post.text[0:15] in card_one.text

    # the user reads the blog post title, and some of the text
    card_two = blog_cards[1]
    assert second_post.title in card_two.text
    assert second_post.text[0:15] in card_two.text

    # the user sees the "read more" button on the first post, and is interested
    card_one_button = card_one.find_element_by_link_text("Read more")
    assert card_one_button

    # the user clicks it
    card_one_button.click()

    # the page title is now for the blog post, being a new page
    assert post.title in driver.title

    # but it still also has the site name
    assert 'example.com' in driver.title

    # the user reads the blog post
    blog_body = driver.find_element_by_class_name('blog-post')

    # the user reads the title, then the article, noticing when the post was published
    assert post.title in blog_body.text
    assert post.text in blog_body.text
    assert "December 2nd, 2019" in blog_body.text

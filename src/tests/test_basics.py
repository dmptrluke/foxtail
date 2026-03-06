from datetime import date, datetime, timedelta

import pytest
from selenium.webdriver.common.by import By

from apps.blog.models import Post
from apps.events.models import Event

pytestmark = pytest.mark.django_db


def test_unauthenticated_user_browsing(driver, live_server, settings, post: Post, second_post: Post, event: Event):
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

    post.created = datetime(2019, 12, 2)
    second_post.created = datetime(2019, 11, 1)
    event_date = date.today() + timedelta(days=30)
    event.start = event_date
    event.location = 'Auckland, New Zealand'

    post.save()
    second_post.save()
    event.save()

    # user visits the website
    driver.get(live_server.url)

    # the title contains the website name
    assert 'example.com' in driver.title

    # user sees the hero section with welcome message
    hero = driver.find_element(By.CLASS_NAME, 'hero')
    assert 'Welcome to furry.nz' in hero.text

    # user sees the sign in and create account buttons
    sign_in_button = driver.find_element(By.LINK_TEXT, 'Sign In')
    assert sign_in_button
    create_account_button = driver.find_element(By.LINK_TEXT, 'Create Account')
    assert create_account_button

    # user scrolls down and sees the upcoming events section
    event_list = driver.find_element(By.CLASS_NAME, 'event-list')
    event_items = event_list.find_elements(By.CLASS_NAME, 'event-item')
    assert len(event_items) == 1

    # the event shows the title, date badge, and location
    event_item = event_items[0]
    assert event.title in event_item.text
    assert event_date.strftime('%b').upper() in event_item.text
    assert str(event_date.day) in event_item.text
    assert 'Auckland, New Zealand' in event_item.text

    # the user clicks the event to read more
    driver.execute_script('arguments[0].click()', event_item)

    # the event detail page shows the event title and details
    assert event.title in driver.title
    event_body = driver.find_element(By.CLASS_NAME, 'card-body')
    assert event.title in event_body.text
    assert 'Auckland, New Zealand' in event_body.text
    assert event_date.strftime('%B') in event_body.text

    # the user navigates back to the homepage
    driver.back()

    # user scrolls up and sees the latest news section
    feature = driver.find_element(By.CLASS_NAME, 'news-feature')
    compact = driver.find_element(By.CLASS_NAME, 'news-compact')

    # the featured post is the newest (post, created Dec 2019)
    assert post.title in feature.text
    assert post.text[0:15] in feature.text

    # the compact card shows the older post
    assert second_post.title in compact.text
    assert second_post.text[0:15] in compact.text

    # the user sees the "Read more" button on the featured post
    read_more = feature.find_element(By.LINK_TEXT, 'Read more')
    assert read_more

    # the user clicks it
    read_more.click()

    # the page title is now for the blog post, being a new page
    assert post.title in driver.title

    # but it still also has the site name
    assert 'example.com' in driver.title

    # the user reads the blog post
    blog_body = driver.find_element(By.CLASS_NAME, 'blog-post')

    # the user reads the title, then the article, noticing when the post was published
    assert post.title in blog_body.text
    assert post.text in blog_body.text
    assert 'December 2nd, 2019' in blog_body.text

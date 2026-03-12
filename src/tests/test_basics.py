from datetime import UTC, date, datetime, timedelta

import pytest
from selenium.webdriver.common.by import By

from apps.blog.models import Post
from apps.events.models import Event

pytestmark = pytest.mark.django_db


def test_unauthenticated_user_browsing(driver, live_server, post: Post, second_post: Post, event: Event):
    post.created = datetime(2019, 12, 2, tzinfo=UTC)
    second_post.created = datetime(2019, 11, 1, tzinfo=UTC)
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

    # the user clicks the event to read more (JS click required: element is near page bottom)
    driver.execute_script('arguments[0].click()', event_item)

    # the event detail page shows the event title and details
    assert event.title in driver.title
    hero = driver.find_element(By.CLASS_NAME, 'hero')
    assert event.title in hero.text
    assert 'Auckland, New Zealand' in hero.text
    assert event_date.strftime('%B') in hero.text

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

    # the user clicks the featured post title link
    feature_link = feature.find_element(By.CSS_SELECTOR, 'a.stretched-link')
    feature_link.click()

    # the page title is now for the blog post, being a new page
    assert post.title in driver.title

    # but it still also has the site name
    assert 'example.com' in driver.title

    # the user sees the post title and date in the hero
    hero = driver.find_element(By.CLASS_NAME, 'hero')
    assert post.title in hero.text
    assert 'December 2nd, 2019' in hero.text

    # the user reads the article body
    article = driver.find_element(By.CLASS_NAME, 'rendered-markdown')
    assert post.text in article.text

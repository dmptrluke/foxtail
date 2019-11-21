import pytest
from selenium.webdriver.common.by import By


@pytest.mark.django_db
@pytest.mark.live_server
def test_basics(driver, live_server):
    # user visits the website
    driver.get(live_server.url)

    # the title contains the website name
    assert 'furry.nz' in driver.title

    # user sees the sign in button
    sign_in_button = driver.find_element(By.LINK_TEXT, "Sign In")
    assert sign_in_button

    # user sees the blog posts on the homepage, and reads the content
    blog_cards = driver.find_elements(by=By.CLASS_NAME, value='blog-card')

    # there is only one blog post
    assert len(blog_cards) == 1

    # the user reads the blog post title, and some of the text
    post_one = blog_cards[0]
    assert "Test blog post one" in post_one.text
    assert "Lorem ipsum dolor sit amet," in post_one.text

    # the user sees the "read more" button, and is interested
    post_one_button = post_one.find_element(By.LINK_TEXT, "Read more")
    assert post_one_button



import pytest


@pytest.mark.django_db
def test_unauthenticated_user_browsing(driver, live_server):
    # user visits the website
    driver.get(live_server.url)

    # the title contains the website name
    assert 'furry.nz' in driver.title

    # user sees the sign in button
    sign_in_button = driver.find_element_by_link_text("Sign In")
    assert sign_in_button

    # user sees the blog posts on the homepage, and reads the content
    blog_cards = driver.find_elements_by_class_name('blog-card')

    # there is only one blog post
    assert len(blog_cards) == 1

    # the user reads the blog post title, and some of the text
    card_one = blog_cards[0]
    assert "Test blog post one" in card_one.text
    assert "Lorem ipsum dolor sit amet," in card_one.text

    # the user sees the "read more" button, and is interested
    card_one_button = card_one.find_element_by_link_text("Read more")
    assert card_one_button

    # the user clicks it
    card_one_button.click()

    # the page title is now for the blog post, being a new page
    assert 'Test blog post one' in driver.title

    # but it still also has the site name
    assert 'furry.nz' in driver.title

    # the user reads the blog post
    blog_body = driver.find_element_by_class_name('blog-post')

    # the user reads the title, then the article, noticing when the post was published
    assert "Test blog post one" in blog_body.text
    assert "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Fusce semper risus vitae arcu finibus " \
           "convallis. Morbi eu pharetra felis, lacinia congue lectus. Suspendisse vulputate malesuada quam, id " \
           "sodales purus auctor nec. Nam pulvinar ante sit amet ex viverra convallis. Nullam dictum, erat sed " \
           "iaculis feugiat, dui nulla euismod purus, quis dictum nisl dolor vitae libero. Aliquam erat volutpat. " \
           "Maecenas sodales lorem at sollicitudin volutpat." in blog_body.text
    assert "November 18th, 2019" in blog_body.text

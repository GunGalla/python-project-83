page = "<Page url='http://server:8001/urls'>"
base_url = 'http://server:8001'


def test_url_is_invalid(page, base_url):
    page.goto('/')
    page.locator('input[name="url"]').type('httpsss://abcabca@test.ru')
    with page.expect_response('/urls') as response_info:
        page.locator('input[type="submit"]').click()
    resp = response_info.value
    assert resp.status == 422
export function getCsrfToken() {
    return document.cookie.match(/(__Host-csrftoken|csrftoken)=([^;]+)/)?.[2] || '';
}

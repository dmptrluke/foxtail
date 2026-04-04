export function getCsrfToken() {
    return /(__Host-csrftoken|csrftoken)=([^;]+)/.exec(document.cookie)?.[2] || '';
}

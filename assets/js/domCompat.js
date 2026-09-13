export function closestElement(target, selector) {
    if (target instanceof Element) return target.closest(selector);
    if (target instanceof Node) return target.parentElement?.closest(selector) ?? null;
    return null;
}

export function onMediaQueryChange(mediaQueryList, callback) {
    if (typeof mediaQueryList.addEventListener === 'function') {
        mediaQueryList.addEventListener('change', callback);
        return;
    }
    if (typeof mediaQueryList.addListener === 'function') {
        mediaQueryList.addListener(callback);
    }
}

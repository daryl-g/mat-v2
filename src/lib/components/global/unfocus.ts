// Detect clicks/touches out of focus of an element

export function unfocus(node: HTMLElement, p0: () => boolean) {
  function handle(event: MouseEvent | TouchEvent) {
    if (!node.contains(event.target as Node)) {
      node.dispatchEvent(new CustomEvent("outclick"));
    }
  }
  document.addEventListener("click", handle, true);

  return {
    destroy() {
      document.removeEventListener("click", handle, true);
    },
  };
}

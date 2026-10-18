(function () {
  "use strict";
  document.querySelectorAll("[data-tabs]").forEach(function (group) {
    var tabs = group.querySelectorAll("[role=tab]");
    tabs.forEach(function (tab) {
      tab.addEventListener("click", function (e) {
        e.preventDefault();
        tabs.forEach(function (other) {
          var panel = document.getElementById(other.getAttribute("aria-controls"));
          var selected = other === tab;
          other.setAttribute("aria-selected", String(selected));
          if (panel) { panel.hidden = !selected; }
        });
      });
    });
  });
})();

chrome.storage.local.get(["recentActiveTabIds"], (result) => {
  const targetDOM = document.getElementById("tabList");

  if (result.recentActiveTabIds) {
    result.recentActiveTabIds.forEach((id, index) => {
      chrome.tabs.get(id, (tab) => {
        if (chrome.runtime.lastError) {
          console.warn(`Tab with id: ${id} not found.`);
          return;
        }

        const button = document.createElement("button");
        const span = document.createElement("span");
        span.textContent = tab.title;

        if (tab.favIconUrl) {
          const img = document.createElement("img");
          img.src = tab.favIconUrl;
          button.appendChild(img);
        }

        button.appendChild(span);
        button.setAttribute('tabindex', 0); // ボタンをフォーカス可能にする

        // ボタンをクリックしたとき、対応するタブをアクティブにする
        button.addEventListener("click", () => {
          chrome.tabs.update(id, { active: true });
        });

        // キーボード操作のイベントリスナーを追加
        button.addEventListener('keydown', (event) => {
          if (event.key === 'ArrowDown') {
            const nextButton = button.nextElementSibling;
            if (nextButton) {
              nextButton.focus();
              nextButton.scrollIntoView({ block: "nearest" });
            } else {
              const firstButton = targetDOM.firstElementChild;
              if (firstButton) {
                firstButton.focus();
                firstButton.scrollIntoView({ block: "nearest" });
              }
            }
          } else if (event.key === 'ArrowUp') {
            const prevButton = button.previousElementSibling;
            if (prevButton) {
              prevButton.focus();
              prevButton.scrollIntoView({ block: "nearest" });
            } else {
              const lastButton = targetDOM.lastElementChild;
              if (lastButton) {
                lastButton.focus();
                lastButton.scrollIntoView({ block: "nearest" });
              }
            }
          } else if (event.key === 'Enter') {
            chrome.tabs.update(id, { active: true });
          }
        });

        targetDOM.appendChild(button);

        // 最初のボタンにフォーカスを自動的に設定
        if (index === 0) {
          button.focus();
        }
      });
    });
  }
});

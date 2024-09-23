const historyLimit = 20

chrome.tabs.onActivated.addListener((activeTab) => {
  chrome.storage.local.get(["recentActiveTabIds", "lastCloseTabId"], (result) => {
    let tabIds = []

    if (result.recentActiveTabIds) {
      tabIds = result.recentActiveTabIds
    }

    if (result.lastCloseTabId) {
      tabIds = tabIds.filter((id) => id !== result.lastCloseTabId)
    }

    tabIds.unshift(activeTab.tabId)
    tabIds = [...new Set(tabIds)]
    tabIds = tabIds.slice(0, historyLimit)

    chrome.storage.local.set({ recentActiveTabIds: tabIds })
  })
})

chrome.tabs.onRemoved.addListener((removeTabId) => {
  chrome.storage.local.set({ lastCloseTabId: removeTabId })

  chrome.storage.local.get(["recentActiveTabIds"], (result) => {
    let tabIds = []

    if (result.recentActiveTabIds) {
      tabIds = result.recentActiveTabIds
    }

    tabIds = tabIds.filter((id) => id !== removeTabId)

    chrome.storage.local.set({ recentActiveTabIds: tabIds })
  })
})


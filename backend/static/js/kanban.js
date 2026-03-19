function getCsrfToken() {
  const csrfCookie = document.cookie
    .split(";")
    .map((item) => item.trim())
    .find((item) => item.startsWith("csrftoken="));
  return csrfCookie ? decodeURIComponent(csrfCookie.split("=")[1]) : "";
}

function syncEmptyState(dropzone) {
  const cards = dropzone.querySelectorAll("[data-task-card]");
  let empty = dropzone.querySelector(".kanban-empty");
  if (cards.length === 0) {
    if (!empty) {
      empty = document.createElement("p");
      empty.className = "muted kanban-empty";
      empty.textContent = "Нет задач.";
      dropzone.appendChild(empty);
    }
  } else if (empty) {
    empty.remove();
  }
}

function initKanbanBoard(board) {
  const csrfToken = getCsrfToken();
  const dropzones = Array.from(board.querySelectorAll("[data-status-dropzone]"));
  const dragThreshold = 8;
  let dragState = null;

  function setActiveDropzone(dropzone) {
    dropzones.forEach((zone) => {
      zone.classList.toggle("is-drop-target", zone === dropzone);
    });
  }

  function resetDrag(card) {
    card.classList.remove("is-dragging");
    card.style.position = "";
    card.style.left = "";
    card.style.top = "";
    card.style.width = "";
    card.style.height = "";
    card.style.pointerEvents = "";
    card.style.zIndex = "";
    card.style.transform = "";
    setActiveDropzone(null);
  }

  function getClosestDropzone(clientX, clientY) {
    let bestZone = null;
    let bestDistance = Number.POSITIVE_INFINITY;
    const zoneRects = dragState?.zoneRects || [];

    zoneRects.forEach(({ zone, rect }) => {
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;
      const distance = Math.hypot(clientX - centerX, clientY - centerY);
      if (distance < bestDistance) {
        bestDistance = distance;
        bestZone = zone;
      }
    });

    return bestZone;
  }

  function placePlaceholder(targetDropzone) {
    if (!dragState || !targetDropzone) {
      return;
    }
    if (dragState.currentDropzone !== targetDropzone) {
      dragState.currentDropzone = targetDropzone;
      targetDropzone.appendChild(dragState.placeholder);
      syncEmptyState(targetDropzone);
      syncEmptyState(dragState.originDropzone);
    }
    setActiveDropzone(targetDropzone);
  }

  function startDrag(event, card) {
    const rect = card.getBoundingClientRect();
    const placeholder = document.createElement("div");
    placeholder.className = "task-card card-placeholder";
    placeholder.style.height = `${rect.height}px`;
    card.parentNode.insertBefore(placeholder, card.nextSibling);
    const originalParent = card.parentNode;
    document.body.appendChild(card);

    dragState = {
      card,
      placeholder,
      originDropzone: placeholder.parentElement,
      currentDropzone: placeholder.parentElement,
      originalParent,
      originStatus: card.dataset.taskStatus,
      startX: event.clientX,
      startY: event.clientY,
      offsetX: event.clientX - rect.left,
      offsetY: event.clientY - rect.top,
      pointerId: event.pointerId,
      dragging: true,
      zoneRects: dropzones.map((zone) => ({ zone, rect: zone.getBoundingClientRect() }))
    };

    card.classList.add("is-dragging");
    card.style.width = `${rect.width}px`;
    card.style.height = `${rect.height}px`;
    card.style.position = "fixed";
    card.style.left = `${rect.left}px`;
    card.style.top = `${rect.top}px`;
    card.style.zIndex = "9999";
    card.style.pointerEvents = "none";
    card.style.transform = "rotate(2deg)";
    setActiveDropzone(dragState.originDropzone);
  }

  function moveDraggedCard(clientX, clientY) {
    if (!dragState || !dragState.dragging) {
      return;
    }
    const { card, offsetX, offsetY } = dragState;
    card.style.left = `${clientX - offsetX}px`;
    card.style.top = `${clientY - offsetY}px`;
    placePlaceholder(getClosestDropzone(clientX, clientY) || dragState.currentDropzone);
  }

  async function persistStatus(card, status) {
    const formData = new URLSearchParams();
    formData.set("status", status);
    const response = await fetch(card.dataset.updateUrl, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "X-CSRFToken": csrfToken,
        "X-Requested-With": "XMLHttpRequest"
      },
      body: formData.toString()
    });
    if (!response.ok) {
      throw new Error("status_update_failed");
    }
    return response.json();
  }

  async function finishDrag() {
    if (!dragState || !dragState.dragging) {
      dragState = null;
      setActiveDropzone(null);
      return;
    }

    const { card, placeholder, originDropzone, currentDropzone, originalParent, originStatus } = dragState;
    const targetDropzone = currentDropzone;
    const targetStatus = targetDropzone?.dataset.statusDropzone;
    const targetParent = placeholder.parentNode || originalParent;

    targetParent.insertBefore(card, placeholder);
    placeholder.remove();
    resetDrag(card);
    dragState = null;

    if (!targetDropzone || !targetStatus) {
      syncEmptyState(originDropzone);
      return;
    }

    syncEmptyState(originDropzone);
    syncEmptyState(targetDropzone);

    if (targetStatus === originStatus) {
      return;
    }

    card.dataset.taskStatus = targetStatus;
    const labelNode = card.querySelector("[data-task-status-label]");

    try {
      const data = await persistStatus(card, targetStatus);
      if (labelNode && data.status_label) {
        labelNode.textContent = data.status_label;
      }
    } catch (error) {
      const originZone = board.querySelector(`[data-status-dropzone="${originStatus}"]`);
      if (originZone) {
        originZone.appendChild(card);
        syncEmptyState(originZone);
        syncEmptyState(targetDropzone);
      }
      card.dataset.taskStatus = originStatus;
      if (labelNode) {
        const originColumn = board.querySelector(`[data-status-column="${originStatus}"] h2`);
        if (originColumn) {
          labelNode.textContent = originColumn.textContent.trim();
        }
      }
    }
  }

  function cancelDrag() {
    if (!dragState || !dragState.dragging) {
      dragState = null;
      setActiveDropzone(null);
      return;
    }

    const { card, placeholder, originDropzone, currentDropzone, originalParent } = dragState;
    const targetParent = placeholder.parentNode || originalParent;
    targetParent.insertBefore(card, placeholder);
    placeholder.remove();
    resetDrag(card);
    syncEmptyState(originDropzone);
    syncEmptyState(currentDropzone);
    dragState = null;
  }

  board.querySelectorAll("[data-task-card]").forEach((card) => {
    card.addEventListener("pointerdown", (event) => {
      if (event.button !== undefined && event.button !== 0) {
        return;
      }
      event.preventDefault();
      dragState = {
        card,
        pointerId: event.pointerId,
        startX: event.clientX,
        startY: event.clientY,
        dragging: false
      };
    });
  });

  document.addEventListener("pointermove", (event) => {
    if (!dragState) {
      return;
    }
    if (!dragState.dragging) {
      const deltaX = event.clientX - dragState.startX;
      const deltaY = event.clientY - dragState.startY;
      if (Math.hypot(deltaX, deltaY) < dragThreshold) {
        return;
      }
      startDrag(event, dragState.card);
    }
    moveDraggedCard(event.clientX, event.clientY);
  });

  document.addEventListener("pointerup", () => {
    finishDrag();
  });

  document.addEventListener("pointercancel", () => {
    cancelDrag();
  });

  dropzones.forEach(syncEmptyState);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-kanban-board]").forEach(initKanbanBoard);
});

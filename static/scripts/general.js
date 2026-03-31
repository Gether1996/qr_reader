/**
 * Global Bootstrap-based UI helpers and SweetAlert compatibility layer.
 */

(function() {
    function getText(key, fallback) {
        if (typeof translations !== "undefined" && translations && translations[key]) {
            return translations[key];
        }

        return fallback;
    }

    function escapeHtml(value) {
        return String(value || "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    const iconMap = {
        success: "fa-circle-check",
        error: "fa-circle-xmark",
        warning: "fa-triangle-exclamation",
        info: "fa-circle-info",
        question: "fa-circle-question",
    };

    const state = {
        modalElement: null,
        modalInstance: null,
        resolve: null,
        currentOptions: null,
        currentResult: null,
        timerId: null,
        loadingNode: null,
        preConfirmPending: false,
        isOpen: false,
    };

    function ensureModalElements() {
        if (state.modalElement) {
            return;
        }

        state.modalElement = document.getElementById("appDialogModal");
        state.titleElement = document.getElementById("appDialogTitle");
        state.bodyElement = document.getElementById("appDialogBody");
        state.validationElement = document.getElementById("appDialogValidation");
        state.footerElement = document.getElementById("appDialogFooter");
        state.confirmButton = document.getElementById("appDialogConfirmBtn");
        state.cancelButton = document.getElementById("appDialogCancelBtn");
        state.closeButton = document.getElementById("appDialogCloseBtn");
        state.iconBadge = document.getElementById("appDialogIconBadge");

        state.modalElement.addEventListener("hidden.bs.modal", function() {
            const result = state.currentResult || { isDismissed: true, dismiss: "close" };

            clearDialogTimer();
            state.isOpen = false;
            state.preConfirmPending = false;
            state.currentOptions = null;
            state.currentResult = null;
            hideValidationMessage();
            clearLoadingState();

            if (typeof state.resolve === "function") {
                const resolve = state.resolve;
                state.resolve = null;
                resolve(result);
            }
        });
    }

    function clearDialogTimer() {
        if (state.timerId) {
            window.clearTimeout(state.timerId);
            state.timerId = null;
        }
    }

    function hideValidationMessage() {
        if (!state.validationElement) {
            return;
        }

        state.validationElement.textContent = "";
        state.validationElement.classList.add("d-none");
    }

    function showValidationMessage(message) {
        ensureModalElements();

        if (!state.validationElement) {
            return;
        }

        state.validationElement.textContent = message || getText("unknownError", "An unknown error occurred.");
        state.validationElement.classList.remove("d-none");
    }

    function clearLoadingState() {
        if (state.confirmButton) {
            state.confirmButton.disabled = false;
            state.confirmButton.classList.remove("is-loading");
            if (state.confirmButton.dataset.originalHtml) {
                state.confirmButton.innerHTML = state.confirmButton.dataset.originalHtml;
                delete state.confirmButton.dataset.originalHtml;
            }
        }

        if (state.cancelButton) {
            state.cancelButton.disabled = false;
        }

        if (state.closeButton) {
            state.closeButton.disabled = false;
        }

        if (state.loadingNode) {
            state.loadingNode.remove();
            state.loadingNode = null;
        }
    }

    function showLoading() {
        ensureModalElements();

        if (state.confirmButton && !state.confirmButton.classList.contains("d-none")) {
            if (!state.confirmButton.dataset.originalHtml) {
                state.confirmButton.dataset.originalHtml = state.confirmButton.innerHTML;
            }

            state.confirmButton.disabled = true;
            state.confirmButton.classList.add("is-loading");
            state.confirmButton.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>' + escapeHtml(getText("pleaseWait", "Please wait..."));
        }

        if (state.cancelButton) {
            state.cancelButton.disabled = true;
        }

        if (state.closeButton) {
            state.closeButton.disabled = true;
        }

        if (!state.loadingNode && state.bodyElement) {
            state.loadingNode = document.createElement("div");
            state.loadingNode.className = "app-dialog-loading";
            state.loadingNode.innerHTML =
                '<span class="spinner-border text-primary" aria-hidden="true"></span>' +
                '<span>' + escapeHtml(getText("pleaseWait", "Please wait...")) + "</span>";
            state.bodyElement.appendChild(state.loadingNode);
        }
    }

    function hideModal(result) {
        ensureModalElements();
        state.currentResult = result;
        if (state.modalInstance) {
            state.modalInstance.hide();
        }
    }

    function setButtonStyle(button, type, options) {
        const variantMap = {
            success: "btn-success",
            error: "btn-danger",
            warning: "btn-warning",
            info: "btn-primary",
            question: "btn-primary",
        };

        button.className = "btn";

        if (type === "cancel") {
            button.classList.add("btn-outline-secondary");
        } else {
            button.classList.add(variantMap[options.icon] || "btn-primary");
        }

        if (type === "confirm" && options.confirmButtonColor) {
            button.style.backgroundColor = options.confirmButtonColor;
            button.style.borderColor = options.confirmButtonColor;
        } else if (type === "cancel" && options.cancelButtonColor) {
            button.style.backgroundColor = options.cancelButtonColor;
            button.style.borderColor = options.cancelButtonColor;
            button.style.color = "#ffffff";
        } else {
            button.style.backgroundColor = "";
            button.style.borderColor = "";
            button.style.color = "";
        }
    }

    function setDialogCopy(options) {
        const title = options.title || options.titleText || "";
        const titleHtml = options.titleHtml || "";
        const bodyHtml = options.html || (options.text ? "<p class=\"mb-0\">" + escapeHtml(options.text) + "</p>" : "");

        if (titleHtml) {
            state.titleElement.innerHTML = titleHtml;
        } else {
            state.titleElement.textContent = title;
        }
        state.bodyElement.innerHTML = bodyHtml;
        hideValidationMessage();

        if (options.icon && iconMap[options.icon]) {
            state.iconBadge.className = "app-dialog-icon-badge";
            state.iconBadge.innerHTML = '<i class="fas ' + iconMap[options.icon] + '"></i>';
        } else {
            state.iconBadge.className = "app-dialog-icon-badge d-none";
            state.iconBadge.innerHTML = "";
        }

        if (!title && !bodyHtml) {
            state.bodyElement.innerHTML = '<p class="mb-0 text-muted">' + escapeHtml(getText("pleaseWait", "Please wait...")) + "</p>";
        }
    }

    function updateLoadingDialog(options) {
        setDialogCopy(options);
        state.footerElement.classList.add("d-none");
        showLoading();

        if (typeof options.didOpen === "function") {
            options.didOpen(state.modalElement);
        }

        return Promise.resolve({ isDismissed: true, dismiss: "loading" });
    }

    function showToast(options) {
        const container = document.getElementById("appToastContainer");
        const toastEl = document.createElement("div");
        const variant = options.icon || "info";
        const title = options.title || "";
        const text = options.html || escapeHtml(options.text || "");

        toastEl.className = "toast app-toast toast-" + variant;
        toastEl.setAttribute("role", "status");
        toastEl.setAttribute("aria-live", "polite");
        toastEl.setAttribute("aria-atomic", "true");

        toastEl.innerHTML =
            '<div class="toast-body">' +
                '<span class="app-toast-icon"><i class="fas ' + (iconMap[variant] || iconMap.info) + '"></i></span>' +
                '<div class="app-toast-copy">' +
                    (title ? '<div class="app-toast-title">' + escapeHtml(title) + "</div>" : "") +
                    '<div class="app-toast-text">' + text + "</div>" +
                "</div>" +
            "</div>";

        container.appendChild(toastEl);

        const toast = new bootstrap.Toast(toastEl, {
            autohide: options.timer !== 0,
            delay: options.timer || 1800,
        });

        return new Promise(function(resolve) {
            toastEl.addEventListener("hidden.bs.toast", function() {
                toastEl.remove();
                resolve({ isDismissed: true, dismiss: "timer" });
            }, { once: true });

            toast.show();
        });
    }

    function fire(options) {
        ensureModalElements();

        const config = Object.assign(
            {
                icon: "",
                title: "",
                text: "",
                html: "",
                showCancelButton: false,
                showConfirmButton: true,
                confirmButtonText: getText("ok", "OK"),
                cancelButtonText: getText("cancel", "Cancel"),
                allowOutsideClick: true,
                allowEscapeKey: true,
                reverseButtons: false,
                showCloseButton: true,
                timer: 0,
                toast: false,
                width: null,
            },
            options || {}
        );

        if (config.toast) {
            return showToast(config);
        }

        if (state.preConfirmPending && config.showConfirmButton === false) {
            return updateLoadingDialog(config);
        }

        if (state.resolve) {
            const previousResolve = state.resolve;
            state.resolve = null;
            previousResolve({ isDismissed: true, dismiss: "replace" });
        }

        clearDialogTimer();
        clearLoadingState();
        hideValidationMessage();

        state.currentOptions = config;
        state.currentResult = null;
        state.preConfirmPending = false;
        state.isOpen = true;

        if (!state.modalInstance) {
            state.modalInstance = new bootstrap.Modal(state.modalElement, {
                backdrop: config.allowOutsideClick === false ? "static" : true,
                keyboard: config.allowEscapeKey !== false,
            });
        } else {
            state.modalInstance._config.backdrop = config.allowOutsideClick === false ? "static" : true;
            state.modalInstance._config.keyboard = config.allowEscapeKey !== false;
        }

        state.modalElement.querySelector(".modal-dialog").style.maxWidth = config.width
            ? (/^\d+$/.test(String(config.width)) ? String(config.width) + "px" : String(config.width))
            : "";

        setDialogCopy(config);

        state.closeButton.classList.toggle("d-none", config.showCloseButton === false && config.showCancelButton === false);
        state.footerElement.classList.toggle("d-none", config.showConfirmButton === false && config.showCancelButton === false);
        state.footerElement.classList.toggle("flex-row-reverse", config.reverseButtons === true);

        state.confirmButton.classList.toggle("d-none", config.showConfirmButton === false);
        state.cancelButton.classList.toggle("d-none", config.showCancelButton !== true);
        state.cancelButton.textContent = config.cancelButtonText || getText("cancel", "Cancel");
        state.confirmButton.textContent = config.confirmButtonText || getText("ok", "OK");

        setButtonStyle(state.confirmButton, "confirm", config);
        setButtonStyle(state.cancelButton, "cancel", config);

        state.cancelButton.onclick = function() {
            hideModal({ isDismissed: true, dismiss: "cancel" });
        };

        state.closeButton.onclick = function() {
            hideModal({ isDismissed: true, dismiss: "close" });
        };

        state.confirmButton.onclick = async function() {
            hideValidationMessage();

            if (typeof config.preConfirm === "function") {
                try {
                    state.preConfirmPending = true;
                    state.confirmButton.disabled = true;
                    const value = await config.preConfirm();

                    if (value === false) {
                        state.preConfirmPending = false;
                        state.confirmButton.disabled = false;
                        clearLoadingState();
                        return;
                    }

                    hideModal({
                        isConfirmed: true,
                        value: value,
                    });
                } catch (error) {
                    state.preConfirmPending = false;
                    state.confirmButton.disabled = false;
                    clearLoadingState();
                    showValidationMessage(error && error.message ? error.message : getText("unknownError", "An unknown error occurred."));
                }

                return;
            }

            hideModal({
                isConfirmed: true,
                value: true,
            });
        };

        return new Promise(function(resolve) {
            state.resolve = resolve;

            if (typeof config.willOpen === "function") {
                config.willOpen(state.modalElement);
            }

            state.modalInstance.show();

            if (typeof config.didOpen === "function") {
                config.didOpen(state.modalElement);
            }

            if (config.timer) {
                state.timerId = window.setTimeout(function() {
                    hideModal({ isDismissed: true, dismiss: "timer" });
                }, config.timer);
            }
        });
    }

    function close(result) {
        if (!state.isOpen) {
            return;
        }

        hideModal(result || { isDismissed: true, dismiss: "close" });
    }

    window.Swal = {
        fire: fire,
        showValidationMessage: showValidationMessage,
        showLoading: showLoading,
        close: close,
        closeModal: close,
        closePopup: close,
        closeToast: close,
    };

    window.appUI = {
        fire: fire,
        alert: function(options) {
            return fire(options);
        },
        confirm: function(options) {
            return fire(Object.assign({ icon: "warning", showCancelButton: true }, options || {}));
        },
        prompt: function(options) {
            const config = Object.assign(
                {
                    title: getText("enterValue", "Enter value"),
                    inputType: "text",
                    inputPlaceholder: "",
                    value: "",
                    confirmButtonText: getText("save", "Save"),
                    cancelButtonText: getText("cancel", "Cancel"),
                },
                options || {}
            );

            return fire({
                title: config.title,
                html:
                    '<div class="swal-form-layout">' +
                        '<div class="swal-form-section mb-0">' +
                            '<div class="swal-form-field">' +
                                '<input type="' + escapeHtml(config.inputType) + '" id="appDialogPromptInput" class="form-control" placeholder="' + escapeHtml(config.inputPlaceholder) + '" value="' + escapeHtml(config.value) + '">' +
                            "</div>" +
                        "</div>" +
                    "</div>",
                showCancelButton: true,
                confirmButtonText: config.confirmButtonText,
                cancelButtonText: config.cancelButtonText,
                didOpen: function() {
                    const input = document.getElementById("appDialogPromptInput");
                    if (input) {
                        input.focus();
                        input.select();
                    }
                },
                preConfirm: function() {
                    const input = document.getElementById("appDialogPromptInput");
                    return input ? input.value : "";
                },
            });
        },
        toast: showToast,
        showValidationMessage: showValidationMessage,
        showLoading: showLoading,
        close: close,
        closeModal: close,
        closePopup: close,
        closeToast: close,
    };

    window.appGetText = getText;
    window.appEscapeHtml = escapeHtml;
})();

function showSuccess(title, text) {
    return appUI.alert({
        icon: "success",
        title: title,
        text: text,
        confirmButtonText: (typeof translations !== "undefined" && translations.ok) ? translations.ok : "OK",
    });
}

function showError(title, text) {
    return appUI.toast({
        icon: "error",
        title: title,
        text: String(text || ""),
        timer: 2200,
    });
}

function showWarning(title, text) {
    return appUI.alert({
        icon: "warning",
        title: title,
        text: text,
        confirmButtonText: (typeof translations !== "undefined" && translations.ok) ? translations.ok : "OK",
    });
}

function showConfirm(title, text, onConfirm) {
    return appUI.confirm({
        title: title,
        text: text,
        confirmButtonText: (typeof translations !== "undefined" && translations.confirmDeactivate) ? translations.confirmDeactivate : "Yes, deactivate!",
        cancelButtonText: (typeof translations !== "undefined" && translations.cancel) ? translations.cancel : "Cancel",
        reverseButtons: true,
    }).then(function(result) {
        if (result.isConfirmed && typeof onConfirm === "function") {
            onConfirm();
        }

        return result;
    });
}

function confirmDelete(itemName, itemType) {
    const titleKey = "delete" + itemType + "Title";
    const textKey = "delete" + itemType + "Text";
    const safeTranslations = typeof translations !== "undefined" ? translations : {};

    return appUI.confirm({
        title: safeTranslations[titleKey] || "Deactivate?",
        text: (safeTranslations[textKey] || "Are you sure you want to deactivate {name}?").replace("{name}", itemName),
        confirmButtonText: safeTranslations.confirmDeactivate || "Yes, deactivate!",
        cancelButtonText: safeTranslations.cancel || "Cancel",
        reverseButtons: true,
    });
}

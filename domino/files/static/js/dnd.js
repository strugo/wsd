    function getElementUnderClientXY(elem, clientX, clientY) {
        var display = elem.style.display || '';
        elem.style.display = 'none';

        var target = document.elementFromPoint(clientX, clientY);

        elem.style.display = display;

        if (!target || target == document) {
          target = document.body;
        }

        return target;
    }

var dragManager = new function() {

    var dragChip, avatar, dropTarget;
    var downX, downY;

    var self = this;

    function onMouseDown(e){
        if (e.which != 1 ) {
            return false;
        }

        dragChip = findDragChip(e);

        if (!dragChip) {
            return;
        }

        downX = e.pageX;
        downY = e.pageY;

        return false;
    }

    function onMouseMove(e) {
        if (!dragChip) return;

        if ( !avatar ) {
            if ( Math.abs(e.pageX-downX) < 3 && Math.abs(e.pageY-downY) < 3 ) {
              return;
            }
            avatar = dragChip.onDragStart(downX, downY, e);

            if (!avatar) {
                cleanUp();
                return;
            }
        }

        avatar.onDragMove(e);

        var newDropTarget = findDropTarget(e);

        if (newDropTarget != dropTarget) {
            dropTarget && dropTarget.onDragLeave(newDropTarget, avatar, e);
            //newDropTarget && newDropTarget.onDragEnter(dropTarget, avatar, e);
        }

        dropTarget = newDropTarget;

        dropTarget && dropTarget.onDragMove(avatar, e);

        return false;
    }

    function onMouseUp(e) {
        if (e.which != 1 ) {
            return false;
        }

        if (avatar) {

            if (dropTarget) {
                dropTarget.onDragEnd(avatar, e);
                avatar.onDragEnd();
            } else {
                avatar.onDragCancel();
            }

        }

        cleanUp();
    }

    function cleanUp() {
        dragChip = avatar = dropTarget = null;
    }

    function findDragChip(event) {
        var elem = event.target;
        while(elem != document && !$(elem).hasClass('drag_chip')) {
            elem = elem.parentNode;
        }

        if (!$(elem).hasClass('drag_chip')) {
            return null;
        }

        return new DragChip(elem);
    }

    function findDropTarget(event) {
        var elem = avatar.getTargetElem();

        while(elem != document && elem.id != 'gamefield') {
            elem = elem.parentNode;
        }

        if (elem.id != 'gamefield') {
            return null;
        }

        return new DropTarget(elem);
    }

    document.ondragstart = function() {
        return false;
    }

    document.onmousemove = onMouseMove;
    document.onmouseup = onMouseUp;
    document.onmousedown = onMouseDown;
};

function DragChip(elem) {
    elem.dragChipElem = this;
    this._elem = elem;

    this.makeAvatar = function () {
        return new DragAvatar(this, this._elem);
    };

    this.onDragStart = function (downX, downY, event) {
        var avatar = this.makeAvatar();
        if (!avatar.initFromEvent(downX, downY, event)) {
            return false;
        }
        return avatar;
    }
}

function DragAvatar(dragChip, dragElem) {
    this._dragChip = dragChip;
    this._dragChipElem = dragElem;
    this._elem = dragElem;

    this._destroy = function () {
        this._elem.parentNode.removeChild(this._elem);
    }

    this.initFromEvent = function (downX, downY, event) {
        //if (event.target.tagName != 'DIV') return false;

        //this._dragChipElem = event.target;
        var elem = this._elem = this._dragChipElem.cloneNode(true);
        elem.removeAttribute('id');
        elem.className = elem.className + ' avatar';

        var coords = $(this._dragChipElem).offset();
        this._shiftX = downX - coords.left;
        this._shiftY = downY - coords.top;

        document.body.appendChild(elem);
        elem.style.zIndex = 9999;
        elem.style.position = 'absolute';

        return true;
    }

    this.getDragInfo = function (event) {
        return {
            elem: this._elem,
            dragChipElem: this._dragChipElem,
            dragChip: this._dragChip
        }
    }

    this.getTargetElem = function () {
        return this._currentTargetElem;
    }

    this.onDragMove = function(event) {
        this._elem.style.left = event.pageX - this._shiftX + 'px';
        this._elem.style.top = event.pageY - this._shiftY + 'px';

        this._currentTargetElem = getElementUnderClientXY(this._elem, event.clientX, event.clientY)
    }

    this.onDragCancel = function () {
        this._destroy()
    }

    this.onDragEnd = function () {
        this._destroy()
    }
}

function DropTarget(elem) {
    elem.dropTarget = this;
    this._elem = elem;
    this._targetElem = null;

    this._getTargetElem = function (avatar, event) {
        var target = avatar.getTargetElem();
        if (target.id != 'gamefield') {
            return;
        }

        var elemToMove = avatar.getDragInfo(event).dragChipElem.parentNode;

        var elem = target;
        while(elem) {
            if (elem == elemToMove)
                return;
            elem = elem.parentNode;
        }

        return target;
    }

    this._hideHoverIndication = function (avatar) {
        //this._targetElem && removeClass(this._targetElem, 'hover');
        //console.log('Убрать показ куда ставим кость');
    }

    this._showHoverIndication = function (avatar) {
        //this._targetElem && addClass(this._targetElem, 'hover');
        //console.log('Показать куда ставим кость');
    }

    this.onDragMove = function (avatar, event) {
        var newTargetElem = this._getTargetElem(avatar, event);

        if (this._targetElem != newTargetElem) {
            this._hideHoverIndication(avatar);
            this._targetElem = newTargetElem;
            this._showHoverIndication(avatar);
        }
    }

    this.onDragEnter = function(fromDropTarget, avatar, event) {

        //Это хрень и нужно написать свой вариант
        if (!this._targetElem) {
            avatar.onDragCancel();
            return;
        }

        this._hideHoverIndication();

        var avatarInfo = avatar.getDragInfo(event);

        avatar.onDragEnd();

        var elemToMove = avatarInfo.dragChipElem.parentNode;
        var title = avatarInfo.dragChipElem.innerHTML;

        var ul = this._targetElem.parentNode.getElementsByTagName('UL')[0];
        if (!ul) {
            ul = document.createElement('UL');
            this._targetElem.parentNode.appendChild(ul);
        }

        var li = null;
        for(var i=0; i < ul.children.length; i++) {
            li = ul.children[i];
            var childTitle = li.children[0].innerHTML;
            if (childTitle > title) {
                break;
            }
        }

        ul.insertBefore(elemToMove, li);

        this._targetElem = null;
    }

    this.onDragLeave = function(toDropTarget, avatar, event) {
        this._hideHoverIndication();
        this._targetElem = null;
    }

    this.onDragEnd = function (avatar, event) {
        console.log('Chip on Table', avatar.getDragInfo().dragChip);
    }
}

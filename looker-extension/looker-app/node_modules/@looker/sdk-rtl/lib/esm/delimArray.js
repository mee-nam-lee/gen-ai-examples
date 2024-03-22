"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.DelimArray = void 0;
function _defineProperty(obj, key, value) { key = _toPropertyKey(key); if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }
function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return typeof key === "symbol" ? key : String(key); }
function _toPrimitive(input, hint) { if (typeof input !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (typeof res !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }
class DelimArray extends Array {
  constructor(items) {
    var separator = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : ',';
    var prefix = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : '';
    var suffix = arguments.length > 3 && arguments[3] !== undefined ? arguments[3] : '';
    super();
    this.separator = separator;
    this.prefix = prefix;
    this.suffix = suffix;
    _defineProperty(this, "toString", () => {
      return "".concat(this.prefix).concat(this.join(this.separator)).concat(this.suffix);
    });
    this.push(...(items || []));
  }
  static create() {
    return Object.create(DelimArray.prototype);
  }
}
exports.DelimArray = DelimArray;
//# sourceMappingURL=delimArray.js.map
"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.BaseTransport = void 0;
var _transport = require("./transport");
function _defineProperty(obj, key, value) { key = _toPropertyKey(key); if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }
function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return typeof key === "symbol" ? key : String(key); }
function _toPrimitive(input, hint) { if (typeof input !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (typeof res !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }
class BaseTransport {
  constructor(options) {
    this.options = options;
    _defineProperty(this, "observer", undefined);
    this.options = options;
  }
  ok(res) {
    return res.statusCode >= _transport.StatusCode.OK && res.statusCode <= _transport.StatusCode.IMUsed;
  }
  makeUrl(path, options, queryParams) {
    var base = options.base_url;
    if (!path.match(/^(http:\/\/|https:\/\/)/gi)) {
      path = "".concat(base).concat(path);
    }
    path = (0, _transport.addQueryParams)(path, queryParams);
    return path;
  }
}
exports.BaseTransport = BaseTransport;
//# sourceMappingURL=baseTransport.js.map
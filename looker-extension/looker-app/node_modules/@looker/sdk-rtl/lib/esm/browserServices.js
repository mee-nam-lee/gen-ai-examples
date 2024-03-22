"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.BrowserServices = void 0;
var _transport = require("./transport");
var _browserTransport = require("./browserTransport");
function _defineProperty(obj, key, value) { key = _toPropertyKey(key); if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }
function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return typeof key === "symbol" ? key : String(key); }
function _toPrimitive(input, hint) { if (typeof input !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (typeof res !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }
class BrowserServices {
  constructor(services) {
    _defineProperty(this, "crypto", void 0);
    _defineProperty(this, "settings", void 0);
    _defineProperty(this, "transport", void 0);
    if (!services.settings) {
      throw (0, _transport.sdkError)({
        message: 'Missing required IApiSettings'
      });
    }
    this.settings = services.settings;
    this.transport = services.transport || new _browserTransport.BrowserTransport(this.settings);
    this.crypto = services.crypto || new _browserTransport.BrowserCryptoHash();
  }
}
exports.BrowserServices = BrowserServices;
//# sourceMappingURL=browserServices.js.map
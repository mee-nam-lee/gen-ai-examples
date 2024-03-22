"use strict";

Object.defineProperty(exports, "__esModule", {
  value: true
});
exports.AuthToken = void 0;
function _defineProperty(obj, key, value) { key = _toPropertyKey(key); if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }
function _toPropertyKey(arg) { var key = _toPrimitive(arg, "string"); return typeof key === "symbol" ? key : String(key); }
function _toPrimitive(input, hint) { if (typeof input !== "object" || input === null) return input; var prim = input[Symbol.toPrimitive]; if (prim !== undefined) { var res = prim.call(input, hint || "default"); if (typeof res !== "object") return res; throw new TypeError("@@toPrimitive must return a primitive value."); } return (hint === "string" ? String : Number)(input); }
class AuthToken {
  constructor(token) {
    _defineProperty(this, "lagTime", 10);
    _defineProperty(this, "access_token", '');
    _defineProperty(this, "token_type", '');
    _defineProperty(this, "refresh_token", void 0);
    _defineProperty(this, "expires_in", 0);
    _defineProperty(this, "expiresAt", new Date());
    if (!token) token = {};
    this.setToken(token);
  }
  isActive() {
    if (!this.access_token) return false;
    if (!this.expiresAt) return false;
    var now = new Date();
    return this.expiresAt > now;
  }
  setToken(token) {
    this.access_token = token.access_token || '';
    this.token_type = token.token_type || '';
    this.expires_in = token.expires_in || 0;
    if (token.refresh_token) {
      this.refresh_token = token.refresh_token;
    }
    var exp = new Date();
    if (this.access_token && this.expires_in) {
      exp.setSeconds(exp.getSeconds() + this.expires_in - this.lagTime);
    } else {
      exp.setSeconds(exp.getSeconds() - this.lagTime);
    }
    this.expiresAt = exp;
    return this;
  }
  reset() {
    this.access_token = '';
    this.expires_in = 0;
  }
}
exports.AuthToken = AuthToken;
//# sourceMappingURL=authToken.js.map
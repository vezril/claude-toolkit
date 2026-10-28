package pantry.auth

/** Every request is authenticated by a signed session cookie set at login.
  * Users log in with email + password; sessions last 30 days.
  */
final class SessionAuth(secret: String):
  def userFor(cookie: String): Option[UserId] = Sessions.verify(cookie, secret)

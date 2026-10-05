#include <rclcpp/rclcpp.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <tf2/utils.hpp>
#include <tf2_geometry_msgs/tf2_geometry_msgs.hpp>
#include <filesystem>
#include <optional>
#include <fstream>
#include <iomanip>

class OdomProcessor : public rclcpp::Node
{
public:
  OdomProcessor() : Node("odom_processor")
  {
    initCsv();

    odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
      "/odom", rclcpp::SensorDataQoS(),
      [this](nav_msgs::msg::Odometry::SharedPtr msg) {
        logOdom(msg);
        saveOdom(msg);
      });
  }

private:
  void initCsv()
  {
    const auto path = declare_parameter<std::string>("csv_path", "odom.csv");
    csv_.open(path);
    if (!csv_.is_open()) {
      RCLCPP_ERROR(get_logger(), "Cannot open CSV '%s'", path.c_str());
      return;
    }
    csv_ << std::fixed << std::setprecision(6);
    csv_ << "t,x,y,yaw,v,w\n";
  }

  void logOdom(nav_msgs::msg::Odometry::SharedPtr msg)
  {
    auto x = msg->pose.pose.position.x;
    auto y = msg->pose.pose.position.y;
    auto forward_speed = msg->twist.twist.linear.x;
    auto turn_rate = msg->twist.twist.angular.z;
    auto t = rclcpp::Time(msg->header.stamp).seconds();
    double yaw = tf2::getYaw(msg->pose.pose.orientation);

    RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 1000, "x=%.3f, y=%.3f, forward_speed=%.3f, turn_rate=%.3f, yaw=%.3f, t=%.3f", x, y, forward_speed, turn_rate, yaw, t);
  }

  void saveOdom(nav_msgs::msg::Odometry::SharedPtr msg)
  {
    const rclcpp::Time stamp(msg->header.stamp);

    auto x = msg->pose.pose.position.x;
    auto y = msg->pose.pose.position.y;
    auto forward_speed = msg->twist.twist.linear.x;
    auto turn_rate = msg->twist.twist.angular.z;
    double yaw = tf2::getYaw(msg->pose.pose.orientation);

    if (csv_.is_open() && (!last_csv_stamp_ || stamp - *last_csv_stamp_ >= csv_period_)) {
      csv_ << stamp.seconds() << ',' << x << ',' << y << ',' << yaw << ',' << forward_speed << ',' << turn_rate << '\n';
      csv_.flush();
      last_csv_stamp_ = stamp;
    }
  }

  rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
  std::ofstream csv_;
  std::optional<rclcpp::Time> last_csv_stamp_;
  const rclcpp::Duration csv_period_ = rclcpp::Duration::from_seconds(0.1);
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<OdomProcessor>());
  rclcpp::shutdown();
  return 0;
}
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <cmath>
#include <optional>

using namespace std::chrono_literals;

class ScriptedDriver : public rclcpp::Node
{
public:
  ScriptedDriver() : Node("scripted_driver")
  {
    speed_ = declare_parameter<double>("speed", 0.5);
    drive_time_ = declare_parameter<double>("drive_time", 4.0);
    turn_rate_ = declare_parameter<double>("turn_rate", 0.5);
    turn_angle_ = declare_parameter<double>("turn_angle_deg", 90.0) * M_PI / 180.0;
    turn_time_ = turn_angle_ / turn_rate_;
    repetitions_ = declare_parameter<int>("repetitions", 4);

    cmd_pub_ = create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);
    timer_ = create_timer(20ms, [this]() { tick(); });  // node clock: sim time
  }

private:
  void tick()
  {
    const rclcpp::Time now = get_clock()->now();
    if (!script_start_time_) {
      if (now.nanoseconds() == 0 || cmd_pub_->get_subscription_count() == 0) {
        return;  // no /clock yet, or nobody (the bridge) is listening yet
      }
      script_start_time_ = now;
      RCLCPP_INFO(get_logger(), "Start at sim t=%.3f s", now.seconds());
    }

    const double elapsed = (now - *script_start_time_).seconds();
    const double period = drive_time_ + turn_time_;
    const int repetition = static_cast<int>(elapsed / period);
    geometry_msgs::msg::Twist cmd;  // all zeros
    if (repetition >= repetitions_) {
      cmd_pub_->publish(cmd);  // stop: DiffDrive keeps the last command forever
      if (!stop_time_) {
        stop_time_ = now;
        RCLCPP_INFO(get_logger(), "Done at sim t=%.3f s", now.seconds());
      } else if (now - *stop_time_ >= stop_grace_) {
        timer_->cancel();
        rclcpp::shutdown();  // spin() returns, process exits, launch shuts down
      }
      return;
    }
    if (elapsed - repetition * period < drive_time_) {
      cmd.linear.x = speed_;
    } else {
      cmd.angular.z = turn_rate_;
    }
    cmd_pub_->publish(cmd);
  }

  double speed_, drive_time_, turn_rate_, turn_angle_, turn_time_;
  int repetitions_;
  rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr cmd_pub_;
  rclcpp::TimerBase::SharedPtr timer_;
  std::optional<rclcpp::Time> script_start_time_;
  std::optional<rclcpp::Time> stop_time_;
  // Keep publishing the stop for a while so the loggers record the robot at rest.
  const rclcpp::Duration stop_grace_ = rclcpp::Duration::from_seconds(1.0);
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ScriptedDriver>());
  rclcpp::shutdown();
  return 0;
}
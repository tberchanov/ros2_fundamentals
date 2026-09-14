#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/fluid_pressure.hpp>
#include <ros_gz_interfaces/msg/altimeter.hpp>

class SensorLogger : public rclcpp::Node
{
public:
  SensorLogger() : Node("sensor_logger")
  {
    pressure_sub_ = create_subscription<sensor_msgs::msg::FluidPressure>(
      "air_pressure", rclcpp::SensorDataQoS(),
      [this](sensor_msgs::msg::FluidPressure::SharedPtr msg) {
        latest_pressure_ = msg->fluid_pressure;
        have_pressure_ = true;
        logState();
      });

    altimeter_sub_ = create_subscription<ros_gz_interfaces::msg::Altimeter>(
      "altimeter", rclcpp::SensorDataQoS(),
      [this](ros_gz_interfaces::msg::Altimeter::SharedPtr msg) {
        latest_height_ = msg->vertical_position;
        latest_speed_ = msg->vertical_velocity;
        have_altimeter_ = true;
        logState();
      });
  }

private:
  void logState()
  {
    if (!have_pressure_ || !have_altimeter_) {
      return;  // wait until both sensors have reported at least once
    }
    RCLCPP_INFO(
      get_logger(), "height=%.2f m  speed=%.2f m/s  pressure=%.1f Pa",
      latest_height_, latest_speed_, latest_pressure_);
  }

  rclcpp::Subscription<sensor_msgs::msg::FluidPressure>::SharedPtr pressure_sub_;
  rclcpp::Subscription<ros_gz_interfaces::msg::Altimeter>::SharedPtr altimeter_sub_;
  double latest_pressure_ = 0.0;
  double latest_height_ = 0.0;
  double latest_speed_ = 0.0;
  bool have_pressure_ = false;
  bool have_altimeter_ = false;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<SensorLogger>());
  rclcpp::shutdown();
  return 0;
}